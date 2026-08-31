"""
login_page.py

Page Object representing the application's login page.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for the login page."""

    # Locators
    USERNAME_INPUT = (
        By.ID,
        "user-name",
    )

    PASSWORD_INPUT = (
        By.ID,
        "password",
    )

    LOGIN_BUTTON = (
        By.ID,
        "login-button",
    )

    ERROR_MESSAGE = (
        By.CSS_SELECTOR,
        "[data-test='error']",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def enter_username(self, username: str) -> None:
        """Enter username."""
        self.enter_text(self.USERNAME_INPUT, username)

    def enter_password(self, password: str) -> None:
        """Enter password."""
        self.enter_text(self.PASSWORD_INPUT, password)

    def click_login(self) -> None:
        """Click login button."""
        self.click(self.LOGIN_BUTTON)

    def login(
        self,
        username: str,
        password: str,
    ) -> None:
        """
        Perform complete login operation.

        This method represents a business action rather
        than exposing Selenium implementation to the test.
        """
        self.logger.info("Performing login")

        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self) -> str:
        """Return login error message."""
        return self.get_text(self.ERROR_MESSAGE)