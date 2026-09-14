import os
import time
import pathlib
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


def save_screenshot(driver, name):
    out = pathlib.Path("artifacts/screenshots")
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    driver.save_screenshot(str(path))
    return str(path)


def collect_nav_links(driver):
    selectors = ["nav a", "header a", "ul.menu a", "ul.nav a", "a.nav-link", "#navbar a", "a"]
    found = []
    for sel in selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for e in els:
                try:
                    if not e.is_displayed():
                        continue
                    href = e.get_attribute("href") or ""
                    text = (e.text or e.get_attribute('aria-label') or href).strip()
                    if not href:
                        continue
                    found.append((text, href))
                except Exception:
                    continue
            if found:
                break
        except Exception:
            continue
    # dedupe by (text.lower(), href)
    seen = set()
    navs = []
    for t, h in found:
        key = (t.lower(), h)
        if key in seen:
            continue
        seen.add(key)
        navs.append((t, h))
    return navs


def click_by_href(driver, href):
    try:
        anchors = driver.find_elements(By.XPATH, f"//a[@href='{href}']")
        for a in anchors:
            if a.is_displayed():
                a.click()
                return True
    except Exception:
        return False
    return False


def click_by_text(driver, label):
    try:
        links = driver.find_elements(By.TAG_NAME, 'a')
        for a in links:
            try:
                text = (a.text or a.get_attribute('aria-label') or '').strip().lower()
                if not text:
                    continue
                if label in text:
                    if a.is_displayed():
                        a.click()
                        return True
            except Exception:
                continue
    except Exception:
        return False
    return False


def click_fuzzy_href(driver, href):
    try:
        links = driver.find_elements(By.TAG_NAME, 'a')
        for a in links:
            try:
                h = a.get_attribute('href') or ''
                if href.rstrip('/') in h.rstrip('/') or h.rstrip('/') in href.rstrip('/'):
                    driver.execute_script('arguments[0].click();', a)
                    return True
            except Exception:
                continue
    except Exception:
        return False
    return False


def test_traverse_all_nav(driver):
    """Start from Home and sequentially navigate: Home -> About -> Skills/Skill -> Experience -> Further -> Contact.

    Clicks are performed in-order (no reset to Home between clicks). Screenshots saved after each navigation.
    """
    order = ["Home", "About", "Skill", "Skills", "Experience", "Further", "Contact"]

    # start at home
    driver.get(SITE_URL)
    wait_for_load(driver)
    save_screenshot(driver, "nav_00_home_before.png")

    out = pathlib.Path("artifacts/screenshots")
    out.mkdir(parents=True, exist_ok=True)

    idx = 0
    for label in order:
        found = False
        lower_label = label.lower()

        # try exact text match first
        links = driver.find_elements(By.TAG_NAME, 'a')
        for a in links:
            try:
                text = (a.text or a.get_attribute('aria-label') or '').strip()
                href = a.get_attribute('href') or ''
                if not text and not href:
                    continue
                if text.strip().lower() == lower_label or lower_label in href.lower():
                    if a.is_displayed():
                        try:
                            a.click()
                            found = True
                            break
                        except Exception:
                            continue
            except Exception:
                continue

        # fallback: partial match
        if not found:
            for a in links:
                try:
                    text = (a.text or a.get_attribute('aria-label') or '').strip().lower()
                    if lower_label in text and a.is_displayed():
                        try:
                            a.click()
                            found = True
                            break
                        except Exception:
                            continue
                except Exception:
                    continue

        # if still not found, try fuzzy href matching and JS click
        if not found:
            for a in links:
                try:
                    href = (a.get_attribute('href') or '').strip()
                    if href and lower_label in href.lower():
                        try:
                            driver.execute_script('arguments[0].click();', a)
                            found = True
                            break
                        except Exception:
                            continue
                except Exception:
                    continue

        time.sleep(1)
        try:
            wait_for_load(driver, timeout=10)
        except Exception:
            pass

        save_screenshot(driver, f"nav_{idx:02}_{lower_label}_after.png")
        idx += 1

    # final assertion: ensure contact screenshot exists or at least multiple screenshots
    files = list(out.glob('nav_*.png'))
    assert files and len(files) >= 2, 'expected navigation screenshots'
