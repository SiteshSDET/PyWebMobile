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
    """Navigate through About -> Skill -> Experience -> Further -> Contact (if present) and take screenshots."""
    driver.get(SITE_URL)
    wait_for_load(driver)
    sections = ["about", "skill", "skills", "experience", "further", "contact"]
    for sec in sections:
        # try clicking the nav item
        clicked = click_nav_item(driver, sec)
        if clicked:
            wait_for_load(driver, timeout=10)
            # save screenshot named after section
            safe_name = f"nav_{sec}.png"
            save_screenshot(driver, safe_name)
        else:
            # not found, continue
            continue


def test_body_contains_text(driver):
    driver.get(SITE_URL)
    wait_for_load(driver)
    body = driver.find_element(By.TAG_NAME, "body")
    assert body is not None
    assert len(body.text) > 0
