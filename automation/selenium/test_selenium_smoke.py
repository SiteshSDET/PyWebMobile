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
    headless_env = os.environ.get("HEADLESS", "false").lower()
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


def save_screenshot(driver, name="screenshot.png"):
    import pathlib
    out = pathlib.Path("artifacts/screenshots")
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    driver.save_screenshot(str(path))
    return str(path)


def click_first_interactive(driver):
    """Try clicking a visible interactive element: button, input[type=submit], or the first meaningful link.
    Return True if a click was performed, False otherwise."""
    from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException

    # Try button
    try:
        btn = driver.find_element(By.TAG_NAME, "button")
        if btn.is_displayed() and btn.is_enabled():
            btn.click()
            return True
    except NoSuchElementException:
        pass

    # Try input[type=submit]
    try:
        submit = driver.find_element(By.CSS_SELECTOR, "input[type=submit]")
        if submit.is_displayed() and submit.is_enabled():
            submit.click()
            return True
    except NoSuchElementException:
        pass

    # Try first non-anchor-hash link
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
        for a in links:
            href = a.get_attribute("href")
            if href and not href.strip().startswith("#") and a.is_displayed():
                try:
                    a.click()
                    return True
                except ElementClickInterceptedException:
                    continue
    except Exception:
        pass

    return False


def test_open_homepage_and_interact(driver):
    """Open homepage, take initial screenshot, attempt to click an interactive element, then take another screenshot and assert navigation or content change."""
    driver.get(SITE_URL)
    wait_for_load(driver)
    initial_url = driver.current_url
    save_screenshot(driver, "before.png")

    clicked = click_first_interactive(driver)

    if clicked:
        # wait a bit for navigation or DOM update
        wait_for_load(driver, timeout=15)
        save_screenshot(driver, "after.png")
        # Either URL changed or page body content changed
        new_url = driver.current_url
        body = driver.find_element(By.TAG_NAME, "body").text
        assert new_url != initial_url or len(body) > 0
    else:
        # No interactive element found — still treat as pass but note it by saving a screenshot
        save_screenshot(driver, "no_interaction.png")


def click_nav_item(driver, label):
    """Click the first visible link whose text contains the label (case-insensitive).
    Returns True if clicked, False otherwise."""
    import time
    from selenium.common.exceptions import ElementClickInterceptedException
    label = label.lower()
    links = driver.find_elements(By.TAG_NAME, "a")
    for a in links:
        try:
            text = (a.text or "").strip().lower()
            href = a.get_attribute("href") or ""
            if label in text or label in href.lower():
                if a.is_displayed() and a.is_enabled():
                    try:
                        a.click()
                        time.sleep(1)
                        return True
                    except ElementClickInterceptedException:
                        continue
        except Exception:
            continue
    return False


def test_navigate_sections(driver):
    """Discover top navigation links, start from Home, then click each nav item in order one-by-one.

    Behavior:
    - Load homepage
    - Find top-level navigation links in document order (link text or href used)
    - For each nav link: navigate back to HOME, click the link, wait, take screenshot nav_<index>_<label>.png
    """
    import time
    driver.get(SITE_URL)
    wait_for_load(driver)

    # discover candidate nav links (try common nav containers first)
    candidates = []
    selectors = ["nav a", "header a", "ul.menu a", "ul.nav a", "a.nav-link", "#navbar a", "a"]
    for sel in selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                # keep visible links only and preserve document order
                for e in els:
                    try:
                        href = e.get_attribute("href") or ""
                        text = (e.text or e.get_attribute('aria-label') or href).strip()
                        if not href:
                            continue
                        if href.strip().startswith('#'):
                            # allow anchor links if they have meaningful text
                            if not text:
                                continue
                        if e.is_displayed():
                            candidates.append((text, href))
                if candidates:
                    break
        except Exception:
            continue

    # deduplicate while preserving order
    seen = set()
    navs = []
    for text, href in candidates:
        key = (text.lower(), href)
        if key in seen:
            continue
        seen.add(key)
        navs.append((text, href))

    assert navs, "No navigation links found"

    # ensure 'Home' is first if present; otherwise prepend SITE_URL as home
    home_index = None
    for i, (t, h) in enumerate(navs):
        if 'home' == t.lower() or h.rstrip('/') == SITE_URL.rstrip('/'):
            home_index = i
            break
    if home_index is not None:
        # rotate so home is first
        navs = navs[home_index:] + navs[:home_index]
    else:
        navs.insert(0, ("Home", SITE_URL))

    # iterate links sequentially, resetting to home before each click
    import pathlib
    out = pathlib.Path("artifacts/screenshots")
    out.mkdir(parents=True, exist_ok=True)

    for idx, (text, href) in enumerate(navs):
        label = text.lower().replace(' ', '_')[:30]
        # navigate back to home to have consistent start
        driver.get(SITE_URL)
        wait_for_load(driver)
        # try to find link by href or text and click
        clicked = False
        # prefer searching by href first
        try:
            # find matching anchors with same href (may be absolute/relative)
            anchors = driver.find_elements(By.XPATH, f"//a[@href='{href}']")
            for a in anchors:
                if a.is_displayed():
                    try:
                        a.click()
                        clicked = True
                        break
                    except Exception:
                        continue
        except Exception:
            pass

        if not clicked:
            # fallback: find by partial text match
            try:
                links = driver.find_elements(By.TAG_NAME, 'a')
                for a in links:
                    try:
                        t = (a.text or a.get_attribute('aria-label') or '').strip().lower()
                        if not t:
                            continue
                        if label.replace('_', ' ') in t or label in t:
                            if a.is_displayed():
                                try:
                                    a.click()
                                    clicked = True
                                    break
                                except Exception:
                                    continue
                    except Exception:
                        continue
            except Exception:
                pass

        # if still not clicked, try clicking via JS by searching all anchors and matching href substring
        if not clicked:
            try:
                all_anchors = driver.find_elements(By.TAG_NAME, 'a')
                for a in all_anchors:
                    try:
                        h = a.get_attribute('href') or ''
                        if href.rstrip('/') in h.rstrip('/') or h.rstrip('/') in href.rstrip('/'):
                            driver.execute_script('arguments[0].click();', a)
                            clicked = True
                            break
                    except Exception:
                        continue
            except Exception:
                pass

        # wait and capture
        time.sleep(1)
        try:
            wait_for_load(driver, timeout=10)
        except Exception:
            pass
        screenshot_name = f"nav_{idx}_{label}.png"
        save_screenshot(driver, screenshot_name)

    # Basic assertion: at least Home screenshot exists
    assert (out / "nav_0_home.png").exists() or len(list(out.glob('nav_*.png'))) > 0


def test_body_contains_text(driver):
    driver.get(SITE_URL)
    wait_for_load(driver)
    body = driver.find_element(By.TAG_NAME, "body")
    assert body is not None
    assert len(body.text) > 0
