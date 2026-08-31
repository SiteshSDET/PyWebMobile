"""
wait_utils.py

Centralized explicit wait implementation.
"""

from __future__ import annotations

from typing import Tuple

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


Locator = Tuple[str, str]


class WaitUtils:
    """Reusable explicit wait operations."""

    DEFAULT_TIMEOUT = 15

    def __init__(
        self,
        driver: WebDriver,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(
            driver,
            timeout,
        )

    def wait_for_visibility(
        self,
        locator: Locator,
    ) -> WebElement:
        """Wait until element is visible."""
        return self.wait.until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_clickable(
        self,
        locator: Locator,
    ) -> WebElement:
        """Wait until element is clickable."""
        return self.wait.until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_presence(
        self,
        locator: Locator,
    ) -> WebElement:
        """Wait until element is present in DOM."""
        return self.wait.until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_url_contains(
        self,
        value: str,
    ) -> bool:
        """Wait until URL contains expected value."""
        return self.wait.until(
            EC.url_contains(value)
        )