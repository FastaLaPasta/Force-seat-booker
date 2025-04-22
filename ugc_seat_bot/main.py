# We use Selenium because we are going to use this 'bot' into dynamic Website
# It will get available seat load thanks to JS (That is not possible with BeatifulSoup)
# Besides it will be usefull to interact with the website for potential booking automation !

from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # Use to load browser driver
from selenium.webdriver.common.by import By  # Needed to tell Selenium how to find an element (button..)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait  # Needed to wait for element to load
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import os
import time
from dotenv import load_dotenv

load_dotenv()


EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

def test_driver_setup():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 30)

    # 1. Go to the homepage
    driver.get("https://www.ugc.fr")

    # 2.Accept Cookies if the popup appears
    try:
        # Use of CSS_SELECTOR as it is more flexible and easy to use
        accept_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.hagreed-validate[data-type='accept_all']")))
        accept_button.click()
        time.sleep(1)
        print("Cookies accepted")

        # 3. Click somewhere safe to get ride of potential promotion's pop-up
        ActionChains(driver=driver).move_by_offset(20, 20).click().perform()
        print("Wow ! Pop up just Disapear")
    except:
        print("No cookies popup shown")

    # 4. Click to open the theatre selection menu
    try:
        theatre_menu = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.pseudo-select[data-target='#modal-search-cinema']")))
        theatre_menu.click()
        print("theatre menu opened")

        city_location_menu = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a.accordion-title[href='#quickaccess-10']")))
        city_location_menu.click()
        print('City selection done')

        # 5. Click on the right Theatre
        location_btn = wait.until(EC.element_to_be_clickable(
            (By.ID, "quickAccessCinema_30")))
        location_btn.click()
        print("Location theatre selected")

        # 6. CLick on the moovie
        movie_selection = wait.until(EC.element_to_be_clickable((By.ID, 'goToFilm_5828_info_title')))
        movie_selection.click()
        time.sleep(0.5)
        print('Movie selected')

        # 7. CLick on wanted schedule
        schedule_selection = wait.until(EC.element_to_be_clickable((By.ID, 'goToShowing_330471481717')))
        schedule_selection.click()
        print('schedule selected')
        time.sleep(0.5)
    except Exception as e:
        print("Failed to open/select theatre:", e)
        driver.quit()
        return

    # 8.Connect to your account
    try:
        time.sleep(0.2)
        # Presence_of_element_located wait for the element to be loaded on the page
        # while element_to_be_clickable wait for it to be visible and enabled
        username_field = wait.until(EC.presence_of_element_located((By.ID, 'mail')))
        username_field.clear()
        username_field.send_keys(EMAIL)

        # Fill password
        time.sleep(0.2)
        password_field = wait.until(EC.presence_of_element_located((By.ID, 'password')))
        password_field.clear()
        password_field.send_keys(PASSWORD)

        # Submit Button
        time.sleep(0.2)
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'connectLink')))
        submit_button.click()
        print('Connection creditentials have been submit')
    except Exception as e:
        print(e)

    # 9. Select the payment method
    try:
        time.sleep(5)
        plus_button = driver.find_element(By.CLASS_NAME, "plus")
        plus_button.click()
        print('choose the subscription card')

        # Validate the transaction
        continue_command = wait.until(EC.element_to_be_clickable((By.ID, 'nextStepForm_0')))
        continue_command.click()
        print('We can select our seat, GREAT SUCCESS')
    except Exception as e:
        print('Something goes wrong:', e)

    # 10. Find available seats
    seats = driver.find_elements(By.CSS_SELECTOR, "g.siege")

    available_seats = []
    for seat in seats:
        if 'siege_occupe' not in seat.get_attribute("class"):
            available_seats.append(seat.get_attribute('id'))
    print(available_seats)

    driver.quit()


if __name__ == "__main__":
    test_driver_setup()
