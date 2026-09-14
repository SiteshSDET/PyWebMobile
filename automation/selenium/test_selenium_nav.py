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
    """Start from Home, then click each discovered nav link one-by-one, saving screenshots."""
    driver.get(SITE_URL)
    wait_for_load(driver)
    navs = collect_nav_links(driver)
    assert navs, "no nav links found"

    # prefer Home as first
    home_idx = None
    for i, (t, h) in enumerate(navs):
        if t.strip().lower() == 'home' or h.rstrip('/') == SITE_URL.rstrip('/'):
            home_idx = i
            break
    if home_idx is not None:
        navs = navs[home_idx:] + navs[:home_idx]
    else:
        navs.insert(0, ("Home", SITE_URL))

    for idx, (text, href) in enumerate(navs):
        label = text.strip().lower() or f"link_{idx}"
        # reset to home
        driver.get(SITE_URL)
        wait_for_load(driver)
        save_screenshot(driver, f"nav_{idx:02}_before_{label}.png")

        clicked = click_by_href(driver, href)
        if not clicked:
            clicked = click_by_text(driver, label)
        if not clicked:
            clicked = click_fuzzy_href(driver, href)

        time.sleep(1)
        try:
            wait_for_load(driver, timeout=8)
        except Exception:
            pass
        save_screenshot(driver, f"nav_{idx:02}_after_{label}.png")

    # Assert at least screenshots were produced
    out = pathlib.Path('artifacts/screenshots')
    files = list(out.glob('nav_*'))
    assert files, 'no screenshots saved'
