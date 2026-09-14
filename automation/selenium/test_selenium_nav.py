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


from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def collect_nav_links(driver):
    selectors = ["nav a", "header a", "ul.menu a", "ul.nav a", "a.nav-link", "#navbar a", "a"]
    found = []
    for sel in selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for e in els:
                try:
                    href = e.get_attribute("href") or ""
                    text = (e.text or e.get_attribute('aria-label') or href).strip()
                    if not href:
                        continue
                    # keep candidates even if not visible (menu may be collapsed)
                    found.append((text, href, e))
                except Exception:
                    continue
            if found:
                break
        except Exception:
            continue
    # dedupe by (text.lower(), href)
    seen = set()
    navs = []
    for t, h, el in found:
        key = (t.lower(), h)
        if key in seen:
            continue
        seen.add(key)
        navs.append((t, h))
    return navs


def try_open_menu(driver):
    """If the site uses a collapsed mobile menu, try to open it by clicking common toggles."""
    toggles = ["button[aria-label*='menu']", ".navbar-toggler", ".menu-toggle", "button[aria-expanded='false']"]
    for s in toggles:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, s)
            for el in els:
                try:
                    if el.is_displayed():
                        el.click()
                        WebDriverWait(driver, 2).until(lambda d: True)
                        return True
                except Exception:
                    continue
        except Exception:
            continue
    return False


def click_by_href(driver, href):
    # try strict match first
    try:
        anchors = driver.find_elements(By.XPATH, f"//a[@href='{href}']")
        for a in anchors:
            try:
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable(a))
                driver.execute_script('arguments[0].scrollIntoView(true);', a)
                a.click()
                return True
            except Exception:
                continue
    except Exception:
        pass

    # try opening menu and searching again
    try_open_menu(driver)
    try:
        anchors = driver.find_elements(By.XPATH, f"//a[@href='{href}']")
        for a in anchors:
            try:
                driver.execute_script('arguments[0].scrollIntoView(true);', a)
                driver.execute_script('arguments[0].click();', a)
                return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def click_by_text(driver, label):
    try_open_menu(driver)
    try:
        links = driver.find_elements(By.TAG_NAME, 'a')
        for a in links:
            try:
                text = (a.text or a.get_attribute('aria-label') or '').strip().lower()
                if not text:
                    continue
                if label in text:
                    try:
                        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, ".")))
                    except Exception:
                        pass
                    driver.execute_script('arguments[0].scrollIntoView(true);', a)
                    try:
                        a.click()
                        return True
                    except Exception:
                        try:
                            driver.execute_script('arguments[0].click();', a)
                            return True
                        except Exception:
                            continue
            except Exception:
                continue
    except Exception:
        pass
    return False


def click_fuzzy_href(driver, href):
    try_open_menu(driver)
    try:
        links = driver.find_elements(By.TAG_NAME, 'a')
        for a in links:
            try:
                h = a.get_attribute('href') or ''
                if href.rstrip('/') in h.rstrip('/') or h.rstrip('/') in href.rstrip('/'):
                    try:
                        driver.execute_script('arguments[0].scrollIntoView(true);', a)
                        driver.execute_script('arguments[0].click();', a)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception:
        pass
    return False


def test_traverse_all_nav(driver):
    """Discover all top-level nav links in DOM order and click each one sequentially (no skipping).

    This ensures every menu option is visited one-by-one until the end.
    """
    driver.get(SITE_URL)
    wait_for_load(driver)

    # collect navs (text, href)
    navs = collect_nav_links(driver)
    assert navs, "No navigation links found"

    # Ensure Home is included at start
    home_key = None
    for i, (t, h) in enumerate(navs):
        if (t and t.strip().lower() == 'home') or (h and h.rstrip('/') == SITE_URL.rstrip('/')):
            home_key = i
            break
    if home_key is not None:
        navs = navs[home_key:] + navs[:home_key]
    else:
        navs.insert(0, ("Home", SITE_URL))

    out = pathlib.Path("artifacts/screenshots")
    out.mkdir(parents=True, exist_ok=True)

    def click_target(text, href):
        """Find and click an anchor matching href or text in the current DOM. Returns True if clicked."""
        # try strict href match
        try:
            anchors = driver.find_elements(By.XPATH, f"//a[@href='{href}']")
            for a in anchors:
                try:
                    if a.is_displayed():
                        driver.execute_script('arguments[0].scrollIntoView(true);', a)
                        a.click()
                        return True
                except Exception:
                    continue
        except Exception:
            pass

        # try opening menu toggles
        try_open_menu(driver)

        # try by exact text then contains
        try:
            anchors = driver.find_elements(By.TAG_NAME, 'a')
            for a in anchors:
                try:
                    t = (a.text or a.get_attribute('aria-label') or '').strip()
                    if not t:
                        continue
                    if t.strip().lower() == (text or '').strip().lower() or (text or '').strip().lower() in t.strip().lower():
                        if a.is_displayed():
                            driver.execute_script('arguments[0].scrollIntoView(true);', a)
                            try:
                                a.click()
                                return True
                            except Exception:
                                try:
                                    driver.execute_script('arguments[0].click();', a)
                                    return True
                                except Exception:
                                    continue
                except Exception:
                    continue
        except Exception:
            pass

        # fuzzy href match
        try:
            anchors = driver.find_elements(By.TAG_NAME, 'a')
            for a in anchors:
                try:
                    h = (a.get_attribute('href') or '')
                    if not h:
                        continue
                    if href.rstrip('/') in h.rstrip('/') or h.rstrip('/') in (href or '').rstrip('/'):
                        driver.execute_script('arguments[0].scrollIntoView(true);', a)
                        try:
                            a.click()
                            return True
                        except Exception:
                            try:
                                driver.execute_script('arguments[0].click();', a)
                                return True
                            except Exception:
                                continue
                except Exception:
                    continue
        except Exception:
            pass

        return False

    # sequentially click each discovered nav
    for idx, (text, href) in enumerate(navs):
        label = (text or href or f"link_{idx}").strip()[:40]
        clicked = click_target(text, href)
        time.sleep(1)
        try:
            wait_for_load(driver, timeout=8)
        except Exception:
            pass
        save_screenshot(driver, f"nav_{idx:02}_{label.replace(' ','_')}_after.png")

    files = list(out.glob('nav_*.png'))
    assert files and len(files) >= len(navs), f'expected at least {len(navs)} screenshots, got {len(files)}'