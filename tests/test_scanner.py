import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.scanner import AccessibilityScanner


def _scan_html(html: str) -> dict:
    import tempfile
    import requests
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import threading

    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False)
    tmp.write(html)
    tmp.close()

    served = {}

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode())
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *a):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    scanner = AccessibilityScanner(f"http://127.0.0.1:{port}/")
    result = scanner.scan()
    server.shutdown()
    os.unlink(tmp.name)
    return result


def _scan_html_static(html: str) -> dict:
    from bs4 import BeautifulSoup
    scanner = AccessibilityScanner("http://test.local")
    scanner.soup = BeautifulSoup(html, "html5lib")
    scanner.html_lang = scanner.soup.html.get("lang") if scanner.soup.html else None
    scanner.page_title = scanner.soup.title.string.strip() if scanner.soup.title and scanner.soup.title.string else ""
    scanner.stats["total_elements"] = len(scanner.soup.find_all())
    return scanner


def _run_checks(html: str) -> dict:
    scanner = _scan_html_static(html)
    scanner.check_lang_attribute()
    scanner.check_missing_alt_text()
    scanner.check_heading_structure()
    scanner.check_links()
    scanner.check_duplicate_ids()
    scanner.check_form_labels()
    scanner.check_tables()
    scanner.check_aria_landmarks()
    scanner.check_aria_required_attributes()
    scanner.check_deprecated_elements()
    scanner.check_meta_viewport()
    return scanner.get_report()


def test_perfect_page():
    html = """<!DOCTYPE html>
<html lang="es">
<head><title>Test Page</title><meta name="viewport" content="width=device-width"></head>
<body>
  <header role="banner"><h1>Main Title</h1></header>
  <main><p>Content</p></main>
  <footer>Footer</footer>
</body></html>"""
    report = _run_checks(html)
    assert report["violations"] == 0, f"Expected 0 violations, got {report['violations']}: {report['issues']}"
    assert report["score"] == 100


def test_missing_alt_text():
    html = '<html lang="es"><head><title>T</title></head><body><img src="foto.jpg"></body></html>'
    report = _run_checks(html)
    assert any(i["rule_id"] == "missing-alt" for i in report["issues"])


def test_missing_lang():
    html = '<html><head><title>T</title></head><body><h1>Hola</h1></body></html>'
    report = _run_checks(html)
    assert any(i["rule_id"] == "missing-lang" for i in report["issues"])


def test_skipped_heading():
    html = '<html lang="es"><head><title>T</title></head><body><h1>A</h1><h3>Saltado</h3></body></html>'
    report = _run_checks(html)
    assert any(i["rule_id"] == "skipped-heading" for i in report["issues"])


def test_duplicate_ids():
    html = '<html lang="es"><head><title>T</title></head><body><div id="x"></div><div id="x"></div></body></html>'
    report = _run_checks(html)
    assert any(i["rule_id"] == "duplicate-id" for i in report["issues"])


def test_missing_form_label():
    html = '<html lang="es"><head><title>T</title></head><body><form><input type="text" name="nombre"></form></body></html>'
    report = _run_checks(html)
    assert any(i["rule_id"] == "missing-form-label" for i in report["issues"])


def test_vague_link_text():
    html = '<html lang="es"><head><title>T</title></head><body><a href="/">click here</a></body></html>'
    report = _run_checks(html)
    assert any(i["rule_id"] == "vague-link-text" for i in report["issues"])


def test_no_h1():
    html = '<html lang="es"><head><title>T</title></head><body><h2>Sub</h2></body></html>'
    report = _run_checks(html)
    assert any(i["rule_id"] == "no-h1" for i in report["issues"])


def test_report_structure():
    html = '<html lang="en"><head><title>Test</title><meta name="viewport" content="width=device-width"></head><body><h1>Title</h1></body></html>'
    report = _run_checks(html)
    assert "url" in report
    assert "score" in report
    assert "violations" in report
    assert "passes" in report
    assert "by_impact" in report
    assert "by_principle" in report
    assert "issues" in report
    assert "summary" in report
    assert report["url"] == "http://test.local"
    assert report["title"] == "Test"
