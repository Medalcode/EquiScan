WCAG_PRINCIPLES = {
    "perceivable": "Perceivable - La información debe ser presentada de manera que los usuarios puedan percibirla",
    "operable": "Operable - Los componentes de la interfaz deben ser operables",
    "understandable": "Understandable - La información y operación de la interfaz deben ser comprensibles",
    "robust": "Robust - El contenido debe ser suficientemente robusto para ser interpretado por diversos agentes de usuario",
}

IMPACT_ORDER = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}

def get_impact_level(tag: str) -> str:
    return {"wcag21aa": "critical", "wcag21a": "serious", "best-practice": "moderate"}.get(tag, "minor")

def wcag_metadata(rule_id: str):
    rules = {
        "missing-alt": {
            "wcag": "1.1.1",
            "level": "A",
            "impact": "critical",
            "principle": "perceivable",
            "title": "Non-text Content",
        },
        "missing-lang": {
            "wcag": "3.1.1",
            "level": "A",
            "impact": "critical",
            "principle": "understandable",
            "title": "Language of Page",
        },
        "empty-heading": {
            "wcag": "2.4.6",
            "level": "AA",
            "impact": "serious",
            "principle": "operable",
            "title": "Headings and Labels",
        },
        "skipped-heading": {
            "wcag": "2.4.10",
            "level": "AA",
            "impact": "serious",
            "principle": "operable",
            "title": "Section Headings",
        },
        "empty-link": {
            "wcag": "2.4.4",
            "level": "A",
            "impact": "serious",
            "principle": "operable",
            "title": "Link Purpose (In Context)",
        },
        "vague-link-text": {
            "wcag": "2.4.4",
            "level": "A",
            "impact": "serious",
            "principle": "operable",
            "title": "Link Purpose (In Context)",
        },
        "duplicate-id": {
            "wcag": "4.1.1",
            "level": "A",
            "impact": "moderate",
            "principle": "robust",
            "title": "Parsing",
        },
        "missing-form-label": {
            "wcag": "1.3.1",
            "level": "A",
            "impact": "critical",
            "principle": "perceivable",
            "title": "Info and Relationships",
        },
        "missing-th": {
            "wcag": "1.3.1",
            "level": "A",
            "impact": "serious",
            "principle": "perceivable",
            "title": "Info and Relationships",
        },
        "no-h1": {
            "wcag": "2.4.10",
            "level": "AA",
            "impact": "serious",
            "principle": "operable",
            "title": "Section Headings",
        },
        "redundant-title": {
            "wcag": "2.4.4",
            "level": "A",
            "impact": "minor",
            "principle": "operable",
            "title": "Link Purpose (In Context)",
        },
        "missing-main-landmark": {
            "wcag": "1.3.1",
            "level": "A",
            "impact": "moderate",
            "principle": "robust",
            "title": "Info and Relationships",
        },
        "missing-aria-required": {
            "wcag": "4.1.2",
            "level": "A",
            "impact": "serious",
            "principle": "robust",
            "title": "Name, Role, Value",
        },
        "old-font-element": {
            "wcag": "4.1.1",
            "level": "A",
            "impact": "minor",
            "principle": "robust",
            "title": "Parsing",
        },
        "no-meta-viewport": {
            "wcag": "1.4.4",
            "level": "AA",
            "impact": "moderate",
            "principle": "perceivable",
            "title": "Resize Text",
        },
    }
    return rules.get(rule_id, {"wcag": "N/A", "level": "N/A", "impact": "minor", "principle": "robust", "title": "Custom Check"})
