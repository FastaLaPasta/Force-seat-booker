from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def test_open_ugc():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.ugc.fr/")

    assert "UGC" in driver.title
    driver.quit()


if __name__ == "__main__":
    test_open_ugc()
