# EquiScan ♿

Auditoría de accesibilidad web automatizada. Escanea sitios web contra las Pautas de Accesibilidad para el Contenido Web (WCAG) 2.1 y genera reportes detallados con recomendaciones.

## Funcionalidades

- **Auditoría automática** — Ingresa una URL y obtén un análisis completo de accesibilidad
- **14+ verificaciones WCAG** — Alt text, estructura de encabezados, etiquetas de formularios, landmarks ARIA y más
- **Reportes detallados** — Problemas categorizados por impacto (crítico, serio, moderado, menor) y por principio WCAG
- **Historial** — Todas las auditorías anteriores quedan guardadas para seguimiento
- **Score** — Puntaje general de accesibilidad basado en checks pasados vs totales

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + SQLAlchemy + SQLite |
| Dashboard | Streamlit + Plotly + Pandas |
| Scanner | BeautifulSoup + requests + WCAG static analysis |
| Tests | pytest + httpx (TestClient) |

## Principios WCAG Evaluados

| Principio | Verificaciones |
|-----------|---------------|
| 👁️ Perceptible | Alt text en imágenes, etiquetas de formularios, meta viewport |
| 🖱️ Operable | Estructura de encabezados (h1-h6), texto descriptivo en enlaces |
| 🧠 Comprensible | Atributo lang en `<html>`, elementos HTML semánticos |
| 🔧 Robusto | IDs duplicados, atributos ARIA requeridos, landmarks, elementos obsoletos |

## Estructura

```
EquiScan/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── models.py            # SQLAlchemy ORM (Scan)
│   │   ├── schemas.py           # Pydantic models
│   │   ├── routers/
│   │   │   └── scan_router.py   # POST /api/scan, GET /api/history
│   │   └── services/
│   │       ├── scanner.py       # Core accessibility scanner
│   │       └── rules.py         # WCAG rule definitions & metadata
│   └── requirements.txt
├── dashboard/
│   ├── app.py                   # Streamlit (3 vistas)
│   └── requirements.txt
├── tests/
│   ├── test_scanner.py          # 9 tests unitarios del scanner
│   └── test_api.py              # 6 tests de integración de la API
├── .env.example
├── .gitignore
├── pyproject.toml               # ruff + mypy config
└── README.md
```

## Quick Start

```bash
git clone https://github.com/Medalcode/EquiScan.git
cd EquiScan

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Dashboard (otra terminal)
cd dashboard
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

## API

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/scan` | Ejecutar auditoría (body: `{"url": "..."}`) |
| GET | `/api/history` | Historial de las últimas 50 auditorías |
| GET | `/api/scan/{id}` | Detalle de una auditoría específica |
| GET | `/health` | Health check |

## Tests

```bash
cd backend
pytest ../tests/ -v
```

15 tests (9 scanner + 6 API).

## Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///data/equiscan.db` | URL de conexión a BD |

## Autor

**Jonatthan Medalla** — Ingeniería en Computación e Informática, Inacap

## Licencia

MIT
