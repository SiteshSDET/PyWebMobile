"""
home_page.py

Page Object representing the application's home/inventory page.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage

class HomePage(BasePage):
    """Page Object for the home/inventory page."""

    PAGE_TITLE = (
        By.CSS_SELECTOR,
        ".title",
    )

    MENU_BUTTON = (
        By.ID,
        "react-burger-menu-btn",
    )

    CART_LINK = (
        By.CLASS_NAME,
        "shopping_cart_link",
    )

    PRODUCT_NAMES = (
        By.CLASS_NAME,
        "inventory_item_name",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def get_page_title(self) -> str:
        """Return inventory page heading."""
        return self.get_text(self.PAGE_TITLE)

    def open_menu(self) -> None:
        """Open navigation menu."""
        self.click(self.MENU_BUTTON)

    def open_cart(self) -> None:
        """Navigate to shopping cart."""
        self.click(self.CART_LINK)

    def get_product_names(self) -> list[str]:
        """Return names of all products displayed."""
        elements = self.driver.find_elements(*self.PRODUCT_NAMES)

        return [
            element.text.strip()
            for element in elements
            if element.text.strip()
        ]