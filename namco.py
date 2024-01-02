'''namco.py

This module handles the "host connection" to donderhiroba and provide a valid session token for score queries. With a host connection established, it is possible to query other players' scores.

Cookies are bound to expire soon, so we need to refresh the cookie from time to time.
'''

import orjson
import os
from loguru import logger
from typing import Any, Dict, List, Optional, Union
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Playwright

# Parse config file
with open("config.json", "rb") as f:
    config = orjson.loads(f.read())

DONDERHIROBA_HOST = config["donderhiroba_host"]
DONDERHIROBA_SERVER_TYPE = config["server"]
if DONDERHIROBA_SERVER_TYPE != "international":
    logger.warning("This module is only tested on the international donderhiroba.jp website, and it should not work with any regional servers.")

def _url(path: str) -> str:
    return DONDERHIROBA_HOST + path

class NamcoLoginManager():

    def __init__(self, playwright: Optional[Playwright]=None):
        self._pw = playwright or sync_playwright().start()
        self._browser = None
        self._context = None
        self._page = None
        try:
            self.user_email = config["bandai_namco_login_credentials"]["email"]
            self.user_password = config["bandai_namco_login_credentials"]["password"]
        except KeyError:
            logger.error("Bandai Namco login credentials not found in config.json!")
        logger.debug("NamcoLoginManager will use email '%s' and password '%s'" % (self.user_email, "*" * len(self.user_password)))
        self.cookie = {}
        if os.path.exists(".cookies.json"):
            with open(".cookies.json", "wb") as f:
                self.cookie = orjson.loads(f.read())

    def init(self):
        logger.debug("Initializing NamcoLoginManager...")
        client = self._pw.chromium
        self._browser = client.launch(headless=True)
        self._context = self._browser.new_context()
        self._page = self._context.new_page()
        # Goto login page https://donderhiroba.jp/login.php
        logger.debug("Navigating to donderhiroba login page...")
        self._page.goto(_url("/login.php"))
        # Submit form: document.getElementById('login_form').submit();
        self._page.evaluate("document.getElementById('login_form').submit();")
        # Wait for login page to load (oauth2)
        self._page.wait_for_load_state("networkidle")
        logger.debug("Redirected to BN login page, attempting to fill in credentials...")
        # Fill in email (id=mail) and password (id=pass)
        self._page.fill("#mail", self.user_email)
        self._page.fill("#pass", self.user_password)
        # Click the login button (id=btn-idpw-login)
        self._page.click("#btn-idpw-login")
        # Wait for all redirects to complete
        self._page.main_frame.wait_for_url("**/login_select.php", timeout=10_000)
        logger.debug("Redirected to {}...".format(self._page.url))
        # Check if login is successful. If successful, a login_select.php page will be loaded.
        if "login_select" not in self._page.url:
            logger.error("Bandai Namco login failed! Now on page {}".format(self._page.url))
            return False
        logger.debug("Bandai Namco account login successful, selecting donder card...")
        # Select the first user account by document.getElementById('form_user1').submit()
        self._page.evaluate("document.getElementById('form_user1').submit();")
        # Wait for login to complete
        self._page.wait_for_load_state("networkidle")
        if "index" not in self._page.url:
            logger.error("Donder card selection failed!")
            return False
        logger.success("Perfectly logged in to {}!".format(DONDERHIROBA_HOST))
        # Get cookies
        cookies = self._context.cookies()
        for cookie in cookies:
            self.cookie[cookie["name"]] = cookie["value"]
        self.save_cookies()
        return True
    
    def close(self):
        logger.info("Gracefully closing NamcoLoginManager...")
        self._browser.close()
    
    def save_cookies(self):
        with open(".cookies.json", "wb") as f:
            f.write(orjson.dumps(self.cookies))
    
    @property
    def cookies(self):
        return self.cookie


if __name__ == "__main__":
    with sync_playwright() as p:
        # Create an instance of NamcoLoginManager
        login_manager = NamcoLoginManager(p)

        # Initialize the login manager with the Playwright instance
        login_successful = login_manager.init()

        # Attempt to log in and get cookies
        if login_successful:
            print("Login successful. Cookies:")
            print(login_manager.cookies)
        else:
            print("Login failed.")

        # Close the login manager
        login_manager.close()
