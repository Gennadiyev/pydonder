'''namco_async.py

This module handles the "host connection" to donderhiroba.jp and provide a valid session token for score queries. With a host connection established, it is possible to query other players' scores.

Cookies are bound to expire soon, so we need to refresh the cookie from time to time.
'''

import aiohttp
import asyncio
import orjson
import os
from loguru import logger
from typing import Any, Dict, List, Optional, Union
from bs4 import BeautifulSoup

from playwright.async_api import async_playwright, Playwright

# Parse config file
with open("config.json", "rb") as f:
    config = orjson.loads(f.read())

DONDERHIROBA_HOST = config["donderhiroba_host"]
DONDERHIROBA_SERVER_TYPE = config["server"]
if DONDERHIROBA_SERVER_TYPE != "international":
    logger.warning("This module is only tested on the international donderhiroba.jp website, and it should not work with any regional servers.")


def _url(path: str) -> str:
    return DONDERHIROBA_HOST + path

class NamcoLoginManagerAsync():

    def __init__(self, playwright: Playwright):
        self._pw = playwright
        self._browser: Optional[Playwright] = None
        self._context: Optional[Any] = None
        self._page: Optional[Any] = None
        try:
            self.user_email = config["bandai_namco_login_credentials"]["email"]
            self.user_password = config["bandai_namco_login_credentials"]["password"]
        except KeyError:
            logger.error("Bandai Namco login credentials not found in config.json!")
        logger.info("NamcoLoginManagerAsync will use email '%s' and password '%s'" % (self.user_email, "*" * len(self.user_password)))
        self.cookie = {}

    async def init(self):
        logger.debug("Initializing NamcoLoginManagerAsync...")
        client = self._pw.chromium
        self._browser = await client.launch(headless=True)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()
        # Goto login page https://donderhiroba.jp/login.php
        logger.debug("Navigating to donderhiroba login page...")
        await self._page.goto(_url("/login.php"))
        # Submit form: document.getElementById('login_form').submit();
        await self._page.evaluate("document.getElementById('login_form').submit();")
        # Wait for login page to load (oauth2)
        await self._page.wait_for_load_state("networkidle")
        logger.debug("Redirected to BN login page, attempting to fill in credentials...".format(self._page.url))
        # Fill in email (id=mail) and password (id=pass)
        await self._page.fill("#mail", self.user_email)
        await self._page.fill("#pass", self.user_password)
        # Click the login button (id=btn-idpw-login)
        await self._page.click("#btn-idpw-login")
        # Wait for all redirects to complete
        await self._page.main_frame.wait_for_url("**/login_select.php", timeout=10_000)
        logger.debug("Redirected to {}...", self._page.url)
        # Check if login is successful. If successful, a login_select.php page will be loaded.
        if "login_select" not in self._page.url:
            logger.error("Bandai Namco login failed! Now on page {}".format(self._page.url))
            return False
        logger.debug("Bandai Namco account login successful, selecting donder card...")
        # Select the first user account by document.getElementById('form_user1').submit()
        await self._page.evaluate("document.getElementById('form_user1').submit();")
        # Wait for login to complete
        await self._page.wait_for_load_state("networkidle")
        if "index" not in self._page.url:
            logger.error("Donder card selection failed!")
            return False
        logger.success("Perfectly logged in to {}!".format(DONDERHIROBA_HOST))
        # Get cookies
        cookies = await self._context.cookies()
        for cookie in cookies:
            self.cookie[cookie["name"]] = cookie["value"]
        return True
    
    async def close(self):
        logger.info("Gracefully closing NamcoLoginManagerAsync...")
        await self._browser.close()

    @property
    def cookies(self):
        return self.cookie


if __name__ == "__main__":
    # Test
    loop = asyncio.get_event_loop()

    async def test_login():
        async with async_playwright() as p:
            # Create an instance of NamcoLoginManagerAsync
            login_manager = NamcoLoginManagerAsync(p)

            # Initialize the login manager with the Playwright instance
            login_successful = await login_manager.init()

            # Attempt to log in and get cookies
            if login_successful:
                print("Login successful. Cookies:")
                print(login_manager.cookies)
            else:
                print("Login failed.")

            # Close the login manager
            await login_manager.close()

    # Run the test login function
    loop.run_until_complete(test_login())
