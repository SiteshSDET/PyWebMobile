"""
test_login.py

Login test scenarios.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "test_data"
    / "login_data.json"
)


with DATA_FILE.open(
    "r",
    encoding="utf-8",
) as file:
    LOGIN_DATA = json.load(file)


@pytest.mark.smoke
def test_valid_login(
    driver,
    base_url,
) -> None:
    """Verify that a valid user can log in."""

    login_page = LoginPage(driver)
    home_page = HomePage(driver)

    login_page.open(base_url)

    login_page.login(
        LOGIN_DATA["valid_user"]["username"],
        LOGIN_DATA["valid_user"]["password"],
    )

    assert (
        home_page.get_page_title()
        == "Products"
    )


@pytest.mark.regression
def test_invalid_login(
    driver,
    base_url,
) -> None:
    """Verify error message for invalid login."""

    login_page = LoginPage(driver)

    login_page.open(base_url)

    login_page.login(
        LOGIN_DATA["invalid_user"]["username"],
        LOGIN_DATA["invalid_user"]["password"],
    )

    error_message = (
        login_page.get_error_message()
    )

    assert "Username and password" in error_message