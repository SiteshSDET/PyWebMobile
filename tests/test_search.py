"""
test_search.py

Product/search-related test scenarios.
"""

from __future__ import annotations

import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_products_are_displayed(
    driver,
    base_url,
) -> None:
    """Verify products are displayed after login."""

    login_page = LoginPage(driver)
    home_page = HomePage(driver)

    login_page.open(base_url)

    login_page.login(
        "standard_user",
        "secret_sauce",
    )

    products = home_page.get_product_names()

    assert products, (
        "Expected products to be displayed "
        "after successful login."
    )

    assert len(products) > 0