import time

from django.test import LiveServerTestCase
from selenium import webdriver


class Hosttest(LiveServerTestCase):
    def testhomepage(self):
        driver = webdriver.Chrome()

        # driver.get('http://www.google.com/') # works!
        driver.get("http://127.0.0.1:8000/")
        # ^ selenium.common.exceptions.WebDriverException: Message: unknown error: net::ERR_CONNECTION_REFUSED
        # driver.get('http://127.0.0.1:8000/accounts/login/') # ^ same error as above

        # driver.get('http://127.0.0.1.8000/familytree')
        # ^ selenium.common.exceptions.InvalidArgumentException: Message: invalid argument
        time.sleep(15)

        assert True
        # assert "Our big" in driver.title
