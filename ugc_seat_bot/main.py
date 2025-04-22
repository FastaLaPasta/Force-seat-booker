# We use Selenium because we are going to use this 'bot' into dynamic Website
# It will get available seat load thanks to JS (That is not possible with BeatifulSoup)
# Besides it will be usefull to interact with the website for potential booking automation !

import os
import time
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # Use to load browser driver
from selenium.webdriver.common.by import By  # Needed to tell Selenium how to find an element (button..)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait  # Needed to wait for element to load
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables (like email and password) from the .env file
load_dotenv()

# Get email and password from environment variables
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')


class UGCBookingBot:
    def __init__(self):
        # Initialize WebDriver and WebDriverWait
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.wait = WebDriverWait(self.driver, 30)

    def send_discord_notification(self, message: str):
        webhook_url = os.getenv('WEBHOOK_URL')
        playload = {'content': message}
        try:
            response = requests.post(webhook_url, json=playload)
            if response.status_code == 204:
                print('Discord Notification send!')
            else:
                print("Failed to send Discord message:", response.txt)
        except Exception as e:
            print(f"Discord webhook error: {e}")

    def click_button(self, by, value: str):
        """
        This function waits for a button to become clickable and clicks it.

        :param by: The locator strategy (By.ID, By.CSS_SELECTOR, etc.)
        :param value: The locator value (ID, class name, CSS selector, etc.)
        """
        try:
            button = self.wait.until(EC.element_to_be_clickable((by, value)))
            button.click()
        except Exception as e:
            print(f"Error clicking the button with {by} = {value}: {e}")

    def accept_cookies(self):
        # Accept Cookies if the popup appears
        try:
            self.click_button(By.CSS_SELECTOR, "button.hagreed-validate[data-type='accept_all']")
            time.sleep(1)

            # Click somewhere safe to get rid of potential promotion's pop-up
            ActionChains(self.driver).move_by_offset(20, 20).click().perform()
        except Exception as e:
            print(f"No cookies popup shown: {e}")

    def navigate_to_movie(self):
        # Navigate through website to the movie selection menu
        try:
            self.click_button(By.CSS_SELECTOR, "button.pseudo-select[data-target='#modal-search-cinema']")
            self.click_button(By.CSS_SELECTOR, "a.accordion-title[href='#quickaccess-10']")
            self.click_button(By.ID, "quickAccessCinema_30")
            self.click_button(By.ID, 'goToFilm_5828_info_title')
            self.click_button(By.ID, 'goToShowing_330471481717')
            print("Movie and schedule selected")
        except Exception as e:
            print(f"Failed to navigate to movie: {e}")
            self.driver.quit()

    def login(self):
        # Login to the website
        try:
            time.sleep(0.5)
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, 'mail')))
            username_field.clear()
            username_field.send_keys(EMAIL)

            password_field = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
            password_field.clear()
            password_field.send_keys(PASSWORD)

            time.sleep(2)
            submit_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'connectLink')))
            submit_button.click()
            print('Login credentials submitted')
        except Exception as e:
            print(f"Login error: {e}")

    def select_payment_method(self):
        # Select the payment method and proceed
        try:
            time.sleep(5)
            self.click_button(By.CLASS_NAME, "plus")
            self.click_button(By.ID, 'nextStepForm_0')
            print('We can now select our seat, GREAT SUCCESS')
        except Exception as e:
            print(f"Error selecting payment method: {e}")

    def find_available_seats(self):
        # Find available seats on the page
        seats = self.driver.find_elements(By.CSS_SELECTOR, "g.siege")
        available_seats = []
        for seat in seats:
            if 'siege_occupe' not in seat.get_attribute("class") and 'pmr' not in seat.get_attribute("outerHTML"):
                available_seats.append(seat.get_attribute('id'))
        return available_seats

    def quit_driver(self):
        # Quit the driver once the task is completed
        self.driver.quit()

    def monitor_seats(self, check_interval=180):
        try:
            while True:
                self.driver.refresh()
                time.sleep(3)  # Let JS reload

                available_seats = self.find_available_seats()
                if available_seats:
                    self.send_discord_notification("Available Seats:\n" + "\n".join(available_seats))
                    # return available_seats
                else:
                    print(f'no seat available. retry in {check_interval} seconds...')

                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("Monitoring stopped by user.")
            return available_seats

    def run(self):
        # Go to the homepage and start the process
        self.driver.get("https://www.ugc.fr")
        self.accept_cookies()
        self.navigate_to_movie()
        self.login()
        self.select_payment_method()
        available_seats = self.monitor_seats()
        return available_seats


if __name__ == "__main__":
    # Create the bot instance and run it
    bot = UGCBookingBot()
    available_seats = bot.run()
