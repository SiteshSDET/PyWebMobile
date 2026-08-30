import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.mark.parametrize(
    "search_text",
    ["Selenium", "Python", "Appium"]
)
def test_google_search(search_text):
    driver = webdriver.Chrome()
    driver.get("https://www.google.com")
    search = driver.find_element(By.NAME, "q")
    search.send_keys(search_text)
    search.submit()
    assert search_text.lower() in driver.title.lower()