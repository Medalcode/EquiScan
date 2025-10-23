import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_URL = "http://localhost:8000"

st.set_page_config(page_title="EquiScan", page_icon="♿", layout="wide")

IMPACT_COLORS = {"critical": "#ef476f", "serious": "#ffd166", "moderate": "#118ab2", "minor": "#06d6a0"}
PRINCIPLE_ICONS = {"perceivable": "👁️", "operable": "🖱️", "understandable": "🧠", "robust": "🔧"}


def api_post(path, json=None):
    return requests.post(f"{API_URL}{path}", json=json, timeout=30)


def api_get(path):
    return requests.get(f"{API_URL}{path}", timeout=10)


st.sidebar.title("♿ EquiScan")
st.sidebar.caption("Accessibility Compliance Scanner")

menu = st.sidebar.radio("Menú", ["🔍 Nueva Auditoría", "📋 Historial", "ℹ️ Acerca de"])

if menu == "🔍 Nueva Auditoría":
    st.title("🔍 Auditoría de Accesibilidad Web")

    with st.form("scan"):
        url = st.text_input("URL del sitio a auditar", placeholder="ej: www.ejemplo.cl")
        col1, _ = st.columns([1, 3])
        with col1:
            submit = st.form_submit_button("Auditar", type="primary", use_container_width=True)

    if submit:
        if not url.strip():
            st.error("Ingresa una URL válida")
        else:
            with st.spinner(f"Analizando {url}..."):
                try:
                    r = api_post("/api/scan", json={"url": url})
                    if r.status_code == 200:
                        st.session_state.last_result = r.json()
                        st.rerun()
                    else:
                        st.error(r.json().get("detail", "Error al escanear"))
                except requests.ConnectionError:
                    st.error(f"No se pudo conectar al backend en {API_URL}. ¿Está corriendo?")

    if "last_result" in st.session_state:
        result = st.session_state.last_result

        score = result["score"]
        if score >= 90:
            color = "#06d6a0"
            label = "Excelente"
        elif score >= 70:
            color = "#ffd166"
            label = "Regular"
        else:
            color = "#ef476f"
            label = "Necesita Mejoras"

        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(
            f"<div style='text-align:center;padding:1rem;border-radius:10px;background:{color}20;border:2px solid {color}'>"
            f"<h1 style='color:{color};margin:0'>{score:.0f}%</h1>"
            f"<p style='margin:0'><strong>{label}</strong></p></div>",
            unsafe_allow_html=True,
        )
        col2.metric("✅ Checks Pasados", result["passes"], help="Total de verificaciones superadas")
        col3.metric("❌ Violaciones", result["violations"], help="Total de problemas encontrados")
        col4.metric("🌐 Elementos Auditados", result["total_checks"], help="Total de elementos analizados")

        st.caption(f"**URL:** {result['url']}  |  **Título:** {result['title']}")

        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        impacts = result.get("by_impact", {})
        col_i1.metric("🔴 Críticos", impacts.get("critical", 0))
        col_i2.metric("🟡 Serios", impacts.get("serious", 0))
        col_i3.metric("🔵 Moderados", impacts.get("moderate", 0))
        col_i4.metric("🟢 Menores", impacts.get("minor", 0))

        st.markdown("### Distribución por Principio WCAG")
        principles = result.get("by_principle", {})
        fig = go.Figure()
        for p, count in principles.items():
            icon = PRINCIPLE_ICONS.get(p, "📋")
            fig.add_trace(go.Bar(
                name=f"{icon} {p.capitalize()}",
                x=[p.capitalize()],
                y=[count],
                text=[f"{count} issues"],
                textposition="outside",
            ))
        fig.update_layout(
            showlegend=False,
            height=250,
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis_title="Violaciones",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Resumen")
        st.info(result.get("summary", ""))

        issues = result.get("issues", [])
        if issues:
            st.markdown("### Problemas Encontrados")
            for issue in issues:
                impact = issue["impact"]
                color = IMPACT_COLORS.get(impact, "#666")
                with st.expander(
                    f"[{impact.upper()}] {issue['title']} — {issue['element']}"
                ):
                    st.markdown(f"**WCAG:** {issue['wcag']} (Nivel {issue['level']})")
                    st.markdown(f"**Principio:** {issue['principle'].capitalize()}")
                    st.markdown(f"**Elemento:** `{issue['element']}`")
                    st.markdown(f"**Descripción:** {issue['description']}")
                    if issue["html_snippet"]:
                        st.code(issue["html_snippet"], language="html")
        else:
            st.success("No se encontraron problemas de accesibilidad. ¡Excelente trabajo!")

elif menu == "📋 Historial":
    st.title("📋 Historial de Auditorías")
    r = api_get("/api/history")
    if r.status_code == 200:
        data = r.json()
        if data:
            df = pd.DataFrame(data)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d-%m-%Y %H:%M")
            for _, row in df.iterrows():
                score_color = "🟢" if row["score"] >= 90 else "🟡" if row["score"] >= 70 else "🔴"
                with st.container(border=True):
                    cols = st.columns([3, 1, 1, 1])
                    cols[0].markdown(f"**{row['url']}**  \n{row['title'] or 'Sin título'}")
                    cols[1].markdown(f"**Score:** {score_color} {row['score']:.0f}%")
                    cols[2].markdown(f"**❌ {row['violations']}**")
                    cols[3].markdown(f"📅 {row['created_at']}")
                    if st.button("Ver detalles", key=f"view_{row['id']}"):
                        r2 = api_get(f"/api/scan/{row['id']}")
                        if r2.status_code == 200:
                            st.session_state.last_result = r2.json()
                            st.switch_page("app.py")
        else:
            st.info("No hay auditorías aún. Realiza una desde 'Nueva Auditoría'.")
    else:
        st.error("Error al obtener historial")

elif menu == "ℹ️ Acerca de":
    st.title("ℹ️ Acerca de EquiScan")
    st.markdown("""
    **EquiScan** es una herramienta de auditoría de accesibilidad web que verifica
    el cumplimiento de las Pautas de Accesibilidad para el Contenido Web (WCAG) 2.1.

    ### Principios WCAG Evaluados

    | Principio | Descripción |
    |-----------|-------------|
    | 👁️ Perceptible | La información debe ser presentada de forma que todos puedan percibirla |
    | 🖱️ Operable | Los componentes de la interfaz deben ser operables por todos |
    | 🧠 Comprensible | La información y operación deben ser comprensibles |
    | 🔧 Robusto | El contenido debe funcionar con diversas tecnologías de asistencia |

    ### Verificaciones Realizadas

    - Atributos `alt` en imágenes
    - Idioma de la página (`lang`)
    - Estructura de encabezados (h1-h6)
    - Texto descriptivo en enlaces
    - IDs duplicados
    - Etiquetas de formularios
    - Estructura de tablas
    - Landmarks ARIA
    - Atributos ARIA requeridos
    - Elementos HTML obsoletos

    ### Tecnología

    - **Backend:** FastAPI + SQLAlchemy + SQLite
    - **Dashboard:** Streamlit + Plotly
    - **Scanner:** BeautifulSoup + análisis WCAG estático

    ---
    **Autor:** Jonatthan Medalla  
    **Licencia:** MIT
    """)
