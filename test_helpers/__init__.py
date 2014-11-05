"""A collection of test helpers for use with Selenium Webdriver functional
tests
"""
from selenium import webdriver
import unittest

# The loggers for these packages spew a lot of garbage by default
import logging
for verbose_logger in (
        "selenium.webdriver.remote.remote_connection", "paramiko.transport",
        "easyprocess", "pyvirtualdisplay.abstractdisplay",
        "selenium.webdriver.remote.remote_connection",):
    logger = logging.getLogger(verbose_logger)
    logger.setLevel(logging.WARNING)


from .page import Page

__version__ = '1.1.2'


class BrowserTestCase(unittest.TestCase):
    """Browser test case that can be used with Selenium Webdriver to
    functionally test a website
    """

    def start_browser(self, driver="Firefox"):
        """Start and return a Selenium Webdriver browser instance
        """
        if not hasattr(self, "_browsers"):
            self._browsers = list()
        try:
            driver = getattr(webdriver, driver)
        except AttributeError:
            supported_drivers = [
                d for d in webdriver.__dict__.keys()
                    if d[0].isupper() and d not in [
                        'ActionChains', 'FirefoxProfile',
                        'ChromeOptions', 'TouchActions',
                        'DesiredCapabilities'
                    ]
            ]
            raise ValueError(
                "No such driver. Choose from: %s" % (
                    ", ".join(supported_drivers),))

        browser = driver()
        self._browsers.append(browser)
        self.addCleanup(browser.close)
        return browser

    @property
    def browser(self):
        """Returns the last browser started"""
        try:
            return self._browsers[-1]
        except (IndexError, AttributeError):
            raise AttributeError(
                "You need to start a browser before you access it")


class HeadlessBrowserTestCase(BrowserTestCase):

    def start_browser(self, size=(800, 600), driver="Firefox", **kwargs):
        if not hasattr(self, "_display"):
            from pyvirtualdisplay import Display
            self._display = Display()
            self._display.start()

        self.addCleanup(self._display.stop)
        return super(
            HeadlessBrowserTestCase, self).start_browser(driver=driver)

    def is_headless(self):
        return True
