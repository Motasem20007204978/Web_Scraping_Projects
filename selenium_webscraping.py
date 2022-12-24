from time import sleep
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



print('driver opened')
driver = webdriver.Firefox()

#driver.minimize_window()
driver.set_window_rect(50, 20, 1200, 650)#set position and size
#driver.set_window_position(50, 0)

driver.get('http://www.google.com')


driver.implicitly_wait(30)# maximum expected time to load element
# waiting for some elements and scripts to load in the page before throwing a TimeoutException
#implicity waiting waits within given time as [0,30] seconds

try:
    WebDriverWait(driver, 30).until(#explicit wait defined before a certain condition to occur within given time
        EC.text_to_be_present_in_element(
            (By.CLASS_NAME, 'progress-label'),#element filteration
            'Completed!'#expected text
        )
    )
except:
    print('this element does not exists')


driver.find_element(By.CLASS_NAME, 'open-search-main-menu').click()

driver.implicitly_wait(5)

search = driver.find_element(By.CLASS_NAME, 'manga-search-field')
search.send_keys('shengeki no kyojin', Keys.RETURN)

sleep(60)

#driver.close()# close onl focussed browser
driver.quit()# close all tabs in browser that opened with driver
print('driver closed')