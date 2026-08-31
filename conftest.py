"""
conftest.py

Global Pytest fixtures and hooks.
"""

from __future__ import annotations

from typing import Any, Generator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from utilities.config_reader import ConfigReader
from utilities.logger import get_logger
from utilities.screenshot import capture_screenshot


logger = get_logger("conftest")


def create_driver() -> WebDriver:
    """
    Create WebDriver based on configuration.

    Browser can be overridden from command line:

        pytest --browser chrome
        pytest --browser firefox
        pytest --browser edge
    """

    browser = ConfigReader.get(
        "browser",
        "name",
    ).lower()

    headless = (
        ConfigReader.get(
            "browser",
            "headless",
        ).lower()
        == "true"
    )

    if browser == "chrome":

        options = ChromeOptions()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")

        driver = webdriver.Chrome(
            options=options
        )

    elif browser == "firefox":

        options = FirefoxOptions()

        if headless:
            options.add_argument("--headless")

        driver = webdriver.Firefox(
            options=options
        )

    elif browser == "edge":

        options = EdgeOptions()

        if headless:
            options.add_argument("--headless=new")

        driver = webdriver.Edge(
            options=options
        )

    else:
        raise ValueError(
            f"Unsupported browser: {browser}"
        )

    driver.implicitly_wait(0)

    if not headless:
        driver.maximize_window()

    return driver


@pytest.fixture
def driver(
    request: pytest.FixtureRequest,
) -> Generator[WebDriver, Any, None]:
    """
    Function-scoped WebDriver fixture.

    A fresh browser is created for every test.
    """

    logger.info(
        "Starting WebDriver for test: %s",
        request.node.name,
    )

    driver_instance = create_driver()

    yield driver_instance

    logger.info(
        "Closing WebDriver for test: %s",
        request.node.name,
    )

    driver_instance.quit()


@pytest.fixture
def base_url() -> str:
    """Return application base URL."""
    return ConfigReader.get(
        "application",
        "base_url",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo,
):
    """
    Pytest hook that captures a screenshot when
    a test fails during the call phase.
    """

    outcome = yield

    report = outcome.get_result()

    if report.when == "call" and report.failed:

        driver_instance = item.funcargs.get(
            "driver"
        )

        if driver_instance:

            try:
                screenshot_path = capture_screenshot(
                    driver_instance,
                    item.nodeid,
                )

                logger.error(
                    "Test failed. Screenshot: %s",
                    screenshot_path,
                )

            except Exception as exc:
                logger.error(
                    "Unable to capture screenshot: %s",
                    exc,
                )