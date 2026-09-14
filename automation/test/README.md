Smoke tests for SITE_URL

Files:
- run_smoke.py — runnable smoke test (no extra deps)
- test_smoke.py — pytest-compatible tests

Usage:
- Run runnable: python3 automation/test/run_smoke.py
- Run pytest (if pytest installed): pytest automation/test/test_smoke.py

The scripts use the SITE_URL environment variable if set, otherwise default to https://siteshsdet.netlify.app/
