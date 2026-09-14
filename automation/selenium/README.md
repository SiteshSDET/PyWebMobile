Selenium smoke tests

Files:
- requirements.txt — Python dependencies (selenium, webdriver-manager, pytest)
- test_selenium_smoke.py — pytest tests that open a headless Chrome browser

Local usage:
1. Create a virtualenv and install dependencies:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r automation/selenium/requirements.txt

2. Run tests (ensure Chrome is installed on your system):
   SITE_URL=https://siteshsdet.netlify.app/ pytest -q automation/selenium/test_selenium_smoke.py

Notes for CI (GitHub Actions):
- The included workflow installs Google Chrome on ubuntu-latest and runs the pytest suite.
- webdriver-manager will download an appropriate chromedriver at test runtime.
