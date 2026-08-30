import time

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get("https://www.google.com/")
driver.find_element(By.NAME, "q").send_keys("naveen automationlabs")
suggestions = driver.find_elements(By.XPATH, "//*[@class='wM6W7d']/span[normalize-space()]")
for suggestion in suggestions:
    if suggestion.text=='naveen automationlabs youtube':
        print(suggestion.text)
        break
time.sleep(2)
driver.quit()