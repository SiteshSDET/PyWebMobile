"""
screenshot.py

Utility for capturing screenshots during test execution.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver


SCREENSHOT_DIR = (
    Path(__file__).resolve().parent.parent
    / "reports"
    / "screenshots"
)

SCREENSHOT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def capture_screenshot(
    driver: WebDriver,
    test_name: str,
) -> str:
    """
    Capture screenshot and return generated file path.
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    safe_test_name = (
        test_name
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    file_path = (
        SCREENSHOT_DIR
        / f"{safe_test_name}_{timestamp}.png"
    )

    driver.save_screenshot(str(file_path))

    return str(file_path)