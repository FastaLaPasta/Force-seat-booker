# We use Selenium because we are going to use this 'bot' into dynamic Website
# It will get available seat load thanks to JS (That is not possible with BeatifulSoup)
# Besides it will be usefull to interact with the website for potential booking automation !


from selenium.webdriver.chrome.service import Service  # Use to load browser driver
from selenium.webdriver.common.by import By  # Needed to tell Selenium how to find an element (button..)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait  # Needed to wait for element to load
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium import webdriver

import requests
import time
import os


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
                print("Failed to send Discord message:", response.text)
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
            time.sleep(1)
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

    def select_city(self, city_input: str):
        """
        Select the city from the user's input.
        """
        city_input = city_input.strip().lower()
        for title in self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.accordion-title"))):
            title_text = title.text.strip().lower()
            if city_input in title_text:
                title.click()
                print(f"Clicked on city: {title.text.strip()}")
                return
        raise ValueError(f"City '{city_input}' not found.")

    def select_cinema(self, cinema_input: str):
        """
        Select the cinema from the user's input.
        """
        cinema_input = cinema_input.strip().lower()
        accordion_contents = self.driver.find_elements(By.CSS_SELECTOR, "div.accordion-content")
        for content in accordion_contents:
            for link in content.find_elements(By.TAG_NAME, "a"):
                link_text = link.text.strip().lower()
                if cinema_input in link_text:
                    print(f"Clicked on cinema: {link.text.strip()}")
                    link.click()
                    return
        raise ValueError(f"Cinema '{cinema_input}' not found.")

    def select_movie(self, movie_title):
        movie_title = movie_title.strip().lower()
        movie_links = self.driver.find_elements(By.CSS_SELECTOR, "a[id^='goToFilm_'][id$='_info_title']")
        for link in movie_links:
            if movie_title in link.text.strip().lower():
                print(f'movie "{link.text.strip()}" has been finded')
                link.click()
                return
        raise ValueError(f"Error selecting movie: '{movie_title}' ")

    def is_element_in_viewport(self, element):
        """Check if the element is in the visible viewport."""
        location = element.location_once_scrolled_into_view
        size = element.size
        viewport_height = self.driver.execute_script("return window.innerHeight;")
        viewport_width = self.driver.execute_script("return window.innerWidth;")

        return 0 <= location['y'] < viewport_height and \
            0 <= location['x'] < viewport_width and \
            location['y'] + size['height'] <= viewport_height and \
            location['x'] + size['width'] <= viewport_width

    def select_date(self, target_date_input):
        target_id = f"nav_date_{target_date_input}"

        try:
            target_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, target_id))
            )

            # Attempt to scroll the element into view
            for _ in range(5):
                self.driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
                time.sleep(0.5)
                if self.is_element_in_viewport(target_element): break

            target_element.click()
            print(f"🎯 Date {target_date_input} selected.")
        except Exception as e:
            print(f"Error selecting date: {e}")

    def select_schedule(self, time_input):
        time_input = time_input.strip()
        buttons = self.driver.find_elements(By.CSS_SELECTOR, "li.position-relative button")
        for btn in buttons:
            try:
                start_time = btn.find_element(By.CSS_SELECTOR, "div.screening-start").text.strip()
                if start_time == time_input:
                    print(f"Clicked on showtime: {start_time}")
                    btn.click()
                    return
            except Exception:
                continue
        raise ValueError(f"No schedule found for time {time_input}")

    def navigate_to_movie(self, city_input: str, cinema_input: str):
        """
        Navigates to the desired cinema based on user input.
        Assumes that the user is on the UGC homepage.
        """
        try:
            # Open cinema selection modal
            self.click_button(By.CSS_SELECTOR, "button.pseudo-select[data-target='#modal-search-cinema']")
            self.select_city(city_input)
            self.select_cinema(cinema_input)
            self.select_date(target_date_input=input('Enter the date you want to book a seat(yyyy-mm-dd): '))
            self.select_movie(movie_title=input('enter the movie u wanna watch: '))
            self.select_schedule(time_input=input('Time (HH:MM): '))
        except Exception as e:
            print(f"Navigation error: {e}")
            self.driver.quit()
        print("Movie and schedule selected")

    def login(self):
        # Login to the website
        try:
            time.sleep(1)
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, 'mail')))
            username_field.clear()
            username_field.send_keys(EMAIL)

            time.sleep(1)
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
                available_seats.append(seat.get_attribute('id').replace('siege_', ""))
        return available_seats

    def quit_driver(self):
        # Quit the driver once the task is completed
        self.driver.quit()

    def monitor_seats(self, check_interval=180):
        try:
            while True:
                time.sleep(3)  # Let JS reload

                available_seats = self.find_available_seats()
                if available_seats:
                    self.send_discord_notification("Available Seats:\n" + "\n".join(available_seats))
                    # return available_seats
                else:
                    print(f'no seat available. retry in {check_interval} seconds...')

                time.sleep(check_interval)
                self.driver.refresh()
        except KeyboardInterrupt:
            print("Monitoring stopped by user.")
            return available_seats

    def run(self):
        # Go to the homepage and start the process
        self.driver.get("https://www.ugc.fr")
        self.accept_cookies()

        cinema = input('cinema: ')
        city = input('city: ')

        self.navigate_to_movie(city, cinema)
        # TODO Need to handle 2000 or more characters message
        # TODO will come later after user's accounts have been implemented
        self.login()
        self.select_payment_method()
        available_seats = self.monitor_seats()
        return available_seats


if __name__ == "__main__":
    # Create the bot instance and run it
    bot = UGCBookingBot()
    available_seats = bot.run()
