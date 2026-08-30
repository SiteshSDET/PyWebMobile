from selenium.webdriver.support.wait import WebDriverWait


def click_element(driver, locator, timeout=10):

    wait = WebDriverWait(driver, timeout)

    element = wait.until(
        EC.element_to_be_clickable(locator)
    )

    element.click()