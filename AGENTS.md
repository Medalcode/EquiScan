# EquiScan — Agent Guide

## Commands
```bash
# From backend/ directory:
pytest ../tests/ -v                         # all 15 tests
pytest ../tests/test_scanner.py -v          # scanner unit tests
pytest ../tests/test_scanner.py::test_perfect_page -v  # single test
uvicorn app.main:app --reload               # start API

# From repo root:
ruff check .                                # lint
```

## Critical Quirks

- **Scanner is 100% static HTML** — uses `requests` + `BeautifulSoup` (`html5lib` parser). No JavaScript execution. SPAs (React, Vue, Angular) appear as empty shells.
- **Tests must run from `backend/` directory** — test files use relative `sys.path.insert(0, '..')`.
- **Two test modes**: `_scan_html()` starts a real HTTP server (used by 2 tests), `_scan_html_static()` bypasses network (used by 7 tests). The network tests can be flaky.
- **`redundant-title` rule** is defined in `rules.py` metadata but **never checked** in `scanner.py`. Do not expect it in results.
- **`.env.example` includes `SECRET_KEY`** but the application never reads it — only `DATABASE_URL` is used.
- **`switch_page("app.py")`** in dashboard's history view navigates to itself (unusual but works).
- **Dashboard depends on backend** at `http://localhost:8000` — start backend first.
- **Database** auto-created at `backend/data/equiscan.db` via `Base.metadata.create_all()` on import.
