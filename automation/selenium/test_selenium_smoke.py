import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

SITE_URL = os.environ.get("SITE_URL", "https://siteshsdet.netlify.app/")


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    # honor HEADLESS env var (default: true) so local dev can see the browser when needed
    headless_env = os.environ.get("HEADLESS", "true").lower()
    headless = headless_env not in ("0", "false", "no")
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def wait_for_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")


def test_open_homepage(driver):
    driver.get(SITE_URL)
    wait_for_load(driver)
    assert "http" in driver.current_url
    assert driver.title is not None


def test_body_contains_text(driver):
    driver.get(SITE_URL)
    wait_for_load(driver)
    body = driver.find_element(By.TAG_NAME, "body")
    assert body is not None
    assert len(body.text) > 0
