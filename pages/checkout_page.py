"""
checkout_page.py

Page Object representing checkout functionality.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Page Object for checkout pages."""

    CHECKOUT_BUTTON = (
        By.ID,
        "checkout",
    )

    FIRST_NAME = (
        By.ID,
        "first-name",
    )

    LAST_NAME = (
        By.ID,
        "last-name",
    )

    POSTAL_CODE = (
        By.ID,
        "postal-code",
    )

    CONTINUE_BUTTON = (
        By.ID,
        "continue",
    )

    FINISH_BUTTON = (
        By.ID,
        "finish",
    )

    COMPLETE_MESSAGE = (
        By.CLASS_NAME,
        "complete-header",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def click_checkout(self) -> None:
        """Click checkout button."""
        self.click(self.CHECKOUT_BUTTON)

    def enter_customer_details(
        self,
        first_name: str,
        last_name: str,
        postal_code: str,
    ) -> None:
        """Enter customer checkout details."""

        self.enter_text(
            self.FIRST_NAME,
            first_name,
        )

        self.enter_text(
            self.LAST_NAME,
            last_name,
        )

        self.enter_text(
            self.POSTAL_CODE,
            postal_code,
        )

    def click_continue(self) -> None:
        """Continue checkout."""
        self.click(self.CONTINUE_BUTTON)

    def click_finish(self) -> None:
        """Finish checkout."""
        self.click(self.FINISH_BUTTON)

    def get_complete_message(self) -> str:
        """Return order completion message."""
        return self.get_text(self.COMPLETE_MESSAGE)