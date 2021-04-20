from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


path ='C:\\webdrivers\\chromedriver.exe'
driver = webdriver.Chrome(path)

driver.get("https://www.google.com/")
print(driver.title)

search = driver.find_element_by_name("q")
search.send_keys("PYTHON")
search.send_keys(Keys.RETURN)

time.sleep(5)





driver.quit()
