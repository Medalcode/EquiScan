import re
import requests
from collections import Counter
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse
from .rules import wcag_metadata, IMPACT_ORDER


class AccessibilityScanner:
    def __init__(self, url: str, timeout: int = 15):
        self.url = url
        self.timeout = timeout
        self.soup = None
        self.page_title = ""
        self.html_lang = None
        self.issues = []
        self.stats = {
            "total_elements": 0,
            "passes": 0,
            "violations": 0,
            "by_impact": {"critical": 0, "serious": 0, "moderate": 0, "minor": 0},
            "by_principle": {"perceivable": 0, "operable": 0, "understandable": 0, "robust": 0},
        }

    def _add_issue(self, rule_id: str, impact: str, element: str, html_snippet: str, description: str):
        meta = wcag_metadata(rule_id)
        self.issues.append({
            "rule_id": rule_id,
            "wcag": meta["wcag"],
            "level": meta["level"],
            "impact": impact,
            "principle": meta["principle"],
            "element": element,
            "html_snippet": html_snippet[:200],
            "description": description,
            "title": meta["title"],
        })
        self.stats["violations"] += 1
        self.stats["by_impact"][impact] = self.stats["by_impact"].get(impact, 0) + 1
        self.stats["by_principle"][meta["principle"]] = self.stats["by_principle"].get(meta["principle"], 0) + 1

    def _get_html_snippet(self, tag) -> str:
        return str(tag)[:200] if tag else ""

    def fetch_page(self) -> bool:
        try:
            headers = {
                "User-Agent": "EquiScan/1.0 (Accessibility Scanner; +https://github.com/Medalcode/EquiScan)",
                "Accept": "text/html,application/xhtml+xml",
            }
            r = requests.get(self.url, headers=headers, timeout=self.timeout)
            r.raise_for_status()
            self.soup = BeautifulSoup(r.text, "html5lib")
            self.page_title = self.soup.title.string.strip() if self.soup.title and self.soup.title.string else ""
            self.html_lang = self.soup.html.get("lang") if self.soup.html else None
            self.stats["total_elements"] = len(self.soup.find_all())
            return True
        except requests.RequestException as e:
            self.issues.append({
                "rule_id": "fetch-error",
                "wcag": "",
                "level": "",
                "impact": "critical",
                "principle": "robust",
                "element": "page",
                "html_snippet": "",
                "description": f"Could not fetch page: {str(e)}",
                "title": "Page Fetch Error",
            })
            return False

    def check_missing_alt_text(self):
        images = self.soup.find_all("img")
        self.stats["passes"] += len(images)
        for img in images:
            alt = img.get("alt")
            if alt is None:
                self._add_issue(
                    "missing-alt", "critical", "<img>",
                    self._get_html_snippet(img),
                    "Image is missing alt attribute. Screen readers cannot describe this image.",
                )
                self.stats["passes"] -= 1

    def check_lang_attribute(self):
        self.stats["passes"] += 1
        if not self.html_lang:
            self._add_issue(
                "missing-lang", "critical", "<html>",
                "<html>",
                "The <html> element is missing the lang attribute. Screen readers cannot determine the page language.",
            )
            self.stats["passes"] -= 1

    def check_heading_structure(self):
        headings = self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        self.stats["passes"] += len(headings)

        if not headings:
            self._add_issue(
                "no-h1", "serious", "headings",
                "",
                "Page has no heading elements (h1-h6). Headings are essential for navigation.",
            )
            self.stats["passes"] -= 1
            return

        has_h1 = any(h.name == "h1" for h in headings)
        if not has_h1:
            self._add_issue(
                "no-h1", "serious", "h1",
                "",
                "Page has no <h1> element. Each page should have exactly one main heading.",
            )
            self.stats["passes"] -= 1

        prev_level = 0
        for h in headings:
            level = int(h.name[1])
            text = h.get_text(strip=True)
            if not text:
                self._add_issue(
                    "empty-heading", "serious", h.name,
                    self._get_html_snippet(h),
                    f"Empty <{h.name}> element. Headings must contain text.",
                )
                self.stats["passes"] -= 1
            if prev_level and level > prev_level + 1:
                self._add_issue(
                    "skipped-heading", "serious", h.name,
                    self._get_html_snippet(h),
                    f"Skipped heading level: <{h.name}> follows <h{prev_level}>. "
                    f"Use <h{prev_level + 1}> instead.",
                )
                self.stats["passes"] -= 1
            prev_level = level

    def check_links(self):
        links = self.soup.find_all("a", href=True)
        self.stats["passes"] += len(links)

        vague = {"click here", "read more", "more", "here", "info", "details", "link", "this", "learn more", "ver más", "más información", "clic aquí", "aquí", "leer más"}
        for a in links:
            text = a.get_text(strip=True).lower()
            href = a["href"]

            if not text and not a.find("img"):
                self._add_issue(
                    "empty-link", "serious", "<a>",
                    self._get_html_snippet(a),
                    "Link has no text content and no image with alt text.",
                )
                self.stats["passes"] -= 1
            elif text in vague:
                self._add_issue(
                    "vague-link-text", "serious", "<a>",
                    self._get_html_snippet(a),
                    f"Link has vague text '{a.get_text(strip=True)}'. Use descriptive link text.",
                )
                self.stats["passes"] -= 1
            elif href.startswith("#"):
                target_id = href[1:]
                if target_id and not self.soup.find(id=target_id):
                    self._add_issue(
                        "empty-link", "moderate", "<a>",
                        self._get_html_snippet(a),
                        f"Link points to '#{target_id}' but no element with that id exists.",
                    )
                    self.stats["passes"] -= 1

    def check_duplicate_ids(self):
        ids = {}
        for elem in self.soup.find_all(id=True):
            eid = elem["id"]
            if eid in ids:
                self._add_issue(
                    "duplicate-id", "moderate", elem.name,
                    self._get_html_snippet(elem),
                    f"Duplicate id '{eid}' found on <{elem.name}> element. IDs must be unique.",
                )
                self.stats["passes"] -= 1
            ids[eid] = elem

    def check_form_labels(self):
        inputs = self.soup.find_all(["input", "textarea", "select"])
        self.stats["passes"] += len(inputs)
        for inp in inputs:
            if inp.name == "input" and inp.get("type") in ("hidden", "submit", "button", "reset", "image"):
                continue
            inp_id = inp.get("id")
            has_label = False
            if inp_id:
                label = self.soup.find("label", attrs={"for": inp_id})
                if label:
                    has_label = True
            if not has_label:
                parent_label = inp.find_parent("label")
                if parent_label:
                    has_label = True
            if not has_label and inp.get("aria-label"):
                has_label = True
            if not has_label and inp.get("aria-labelledby"):
                has_label = True

            if not has_label:
                self._add_issue(
                    "missing-form-label", "critical", f"<{inp.name}>",
                    self._get_html_snippet(inp),
                    f"Form element <{inp.name}> has no associated label.",
                )
                self.stats["passes"] -= 1

    def check_tables(self):
        tables = self.soup.find_all("table")
        for table in tables:
            has_th = bool(table.find("th"))
            if not has_th:
                self._add_issue(
                    "missing-th", "serious", "<table>",
                    self._get_html_snippet(table),
                    "Table has no <th> (header) elements. Data tables should use <th> with scope.",
                )
                self.stats["passes"] -= 1

    def check_aria_landmarks(self):
        landmarks = self.soup.find_all(["header", "nav", "main", "footer", "aside"])
        has_main = any(elem.name == "main" for elem in landmarks)
        if not has_main:
            main_id = self.soup.find(id=re.compile(r".*main.*", re.I))
            main_role = self.soup.find(attrs={"role": "main"})
            if not main_id and not main_role:
                self._add_issue(
                    "missing-main-landmark", "moderate", "main",
                    "",
                    "Page has no <main> element or role='main' landmark. "
                    "This helps screen readers skip to the main content.",
                )

    def check_aria_required_attributes(self):
        roles_with_required = {
            "checkbox": "aria-checked",
            "combobox": "aria-expanded",
            "heading": "aria-level",
            "option": "aria-selected",
            "radio": "aria-checked",
            "slider": "aria-valuenow",
            "spinbutton": "aria-valuenow",
            "switch": "aria-checked",
            "progressbar": "aria-valuenow",
        }
        for elem in self.soup.find_all(attrs={"role": True}):
            role = elem["role"]
            if role in roles_with_required:
                required_attr = roles_with_required[role]
                if not elem.get(required_attr):
                    self._add_issue(
                        "missing-aria-required", "serious", f"<{elem.name}[role={role}]>",
                        self._get_html_snippet(elem),
                        f"Element with role='{role}' is missing required attribute '{required_attr}'.",
                    )

    def check_deprecated_elements(self):
        deprecated = self.soup.find_all(["font", "center", "marquee", "blink", "frame", "frameset"])
        for elem in deprecated:
            self._add_issue(
                "old-font-element", "minor", f"<{elem.name}>",
                self._get_html_snippet(elem),
                f"Deprecated HTML element <{elem.name}> found. Use CSS instead.",
            )

    def check_meta_viewport(self):
        viewport = self.soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            self._add_issue(
                "no-meta-viewport", "moderate", "<meta>",
                "",
                "Page has no <meta name='viewport'> tag. This can prevent text resizing on mobile.",
            )

    def scan(self) -> dict:
        if not self.fetch_page():
            return self.get_report()

        self.check_lang_attribute()
        self.check_missing_alt_text()
        self.check_heading_structure()
        self.check_links()
        self.check_duplicate_ids()
        self.check_form_labels()
        self.check_tables()
        self.check_aria_landmarks()
        self.check_aria_required_attributes()
        self.check_deprecated_elements()
        self.check_meta_viewport()

        return self.get_report()

    def get_report(self) -> dict:
        impact_order = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
        sorted_issues = sorted(self.issues, key=lambda x: impact_order.get(x["impact"], 99))

        total = self.stats["violations"] + self.stats["passes"]
        score = round((self.stats["passes"] / total * 100), 1) if total > 0 else 0

        return {
            "url": self.url,
            "title": self.page_title,
            "score": score,
            "total_checks": total,
            "passes": self.stats["passes"],
            "violations": self.stats["violations"],
            "by_impact": self.stats["by_impact"],
            "by_principle": self.stats["by_principle"],
            "issues": sorted_issues,
            "summary": self._generate_summary(),
        }

    def _generate_summary(self) -> str:
        counts = self.stats["by_impact"]
        parts = []
        if counts.get("critical", 0) > 0:
            parts.append(f"{counts['critical']} critical")
        if counts.get("serious", 0) > 0:
            parts.append(f"{counts['serious']} serious")
        if counts.get("moderate", 0) > 0:
            parts.append(f"{counts['moderate']} moderate")
        if counts.get("minor", 0) > 0:
            parts.append(f"{counts['minor']} minor")
        if parts:
            return f"Found {', '.join(parts)} issue(s). Score: {self.stats['passes']}/{self.stats['passes'] + self.stats['violations']} checks passed."
        return "No accessibility issues found. Great job!"
