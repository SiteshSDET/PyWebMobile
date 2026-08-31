"""
base_page.py

Contains reusable Selenium operations that are common
across all application pages.
"""

from __future__ import annotations

from typing import Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from utilities.logger import get_logger
from utilities.wait_utils import WaitUtils

class BasePage:
    """
    Base class for all Page Object classes.

    Responsibilities:
        - Common browser interactions
        - Element interactions
        - Explicit waits
        - Common page operations

    Page-specific locators and business actions should NOT
    be implemented here.
    """

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WaitUtils(driver)
        self.logger = get_logger(self.__class__.__name__)

    def open(self, url: str) -> None:
        """Navigate to the supplied URL."""
        self.logger.info("Opening URL: %s", url)
        self.driver.get(url)

    def get_title(self) -> str:
        """Return the current page title."""
        return self.driver.title

    def get_current_url(self) -> str:
        """Return the current browser URL."""
        return self.driver.current_url

    def find_element(
        self,
        locator: Tuple[str, str],
    ) -> WebElement:
        """Wait for and return a visible element."""
        return self.wait.wait_for_visibility(locator)

    def click(self, locator: Tuple[str, str]) -> None:
        """Wait for an element and click it."""
        self.logger.info("Clicking element: %s", locator)

        element = self.wait.wait_for_clickable(locator)
        element.click()

    def enter_text(
        self,
        locator: Tuple[str, str],
        text: str,
    ) -> None:
        """Clear an input field and enter text."""
        self.logger.info(
            "Entering text into element: %s",
            locator,
        )

        element = self.wait.wait_for_visibility(locator)
        element.clear()
        element.send_keys(text)

    def get_text(
        self,
        locator: Tuple[str, str],
    ) -> str:
        """Return visible text from an element."""
        element = self.wait.wait_for_visibility(locator)
        return element.text

    def is_displayed(
        self,
        locator: Tuple[str, str],
    ) -> bool:
        """Return True if an element is displayed."""
        try:
            return self.wait.wait_for_visibility(locator).is_displayed()
        except TimeoutException:
            return False

    def select_checkbox(
        self,
        locator: Tuple[str, str],
    ) -> None:
        """Select a checkbox if it is not already selected."""
        element = self.wait.wait_for_visibility(locator)

        if not element.is_selected():
            element.click()

    def take_screenshot(self, file_path: str) -> None:
        """Capture a browser screenshot."""
        self.driver.save_screenshot(file_path)
        self.logger.info("Screenshot saved: %s", file_path)