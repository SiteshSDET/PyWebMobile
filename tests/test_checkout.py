"""
test_checkout.py

Checkout-related test scenarios.
"""

from __future__ import annotations

import pytest

from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.regression
def test_checkout_page_navigation(
    driver,
    base_url,
) -> None:
    """Verify user can navigate to checkout."""

    login_page = LoginPage(driver)
    home_page = HomePage(driver)
    checkout_page = CheckoutPage(driver)

    login_page.open(base_url)

    login_page.login(
        "standard_user",
        "secret_sauce",
    )

    home_page.open_cart()

    checkout_page.click_checkout()

    checkout_page.enter_customer_details(
        first_name="Sitesh",
        last_name="Tester",
        postal_code="560001",
    )

    checkout_page.click_continue()

    checkout_page.click_finish()

    assert (
        checkout_page.get_complete_message()
        == "Thank you for your order!"
    )