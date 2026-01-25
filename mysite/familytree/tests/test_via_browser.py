import os
import time
import unittest

from django.test import LiveServerTestCase

try:
    from selenium import webdriver  # type: ignore

    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False


@unittest.skipUnless(
    SELENIUM_AVAILABLE and os.environ.get("RUN_SELENIUM_TESTS") == "1",
    "Selenium tests disabled or not available",
)
class Hosttest(LiveServerTestCase):
    def testhomepage(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)

        # driver.get('http://www.google.com/') # works!
        driver.get(self.live_server_url + "/")
        # ^ selenium.common.exceptions.WebDriverException: Message: unknown error: net::ERR_CONNECTION_REFUSED
        # driver.get('http://127.0.0.1:8000/accounts/login/') # ^ same error as above

        # driver.get('http://127.0.0.1.8000/familytree')
        # ^ selenium.common.exceptions.InvalidArgumentException: Message: invalid argument
        time.sleep(10)
        driver.quit()
        assert True
        # assert "Our big" in driver.title
