"""
    Keteparaha
    ~~~~~~~~~~

    Keteparaha is a collection of tools to help when functional testing

    It contains utilities that assist with tasks like running a browser in a
    headless environment, or checking that emails have been sent, or a file has
    been uploaded to a server, or common testing flow control like retrying or
    ignoring certain errors.

    :copyright: (c) 2015 by Hansel Dunlop.
    :license: MIT, see LICENSE for more details
"""
from functools import wraps
import math
import os
from selenium import webdriver
from six import reraise
import sys
import time
import unittest

# The loggers for these packages spew a lot of garbage by default
import logging
for verbose_logger in (
        "selenium.webdriver.remote.remote_connection", "paramiko.transport",
        "easyprocess", "pyvirtualdisplay.abstractdisplay",
        "selenium.webdriver.remote.remote_connection",):
    logger = logging.getLogger(verbose_logger)
    logger.setLevel(logging.WARNING)

FRAME_SIZE = (1300, 1080)


def snapshot_on_error(method):
    """A decorator that captures a snapshot of all browsers on error

    By default these are saved in the home directory, to change the
    snapshot location set SNAPSHOT_PATH on the test case. The snapshot
    directory will be created if possible.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """TestCase wrapper for snapshot_on_error"""
        snapshot_path = getattr(self, "SNAPSHOT_PATH", os.path.expanduser("~"))
        if not os.path.exists(snapshot_path):
            os.makedirs(snapshot_path)
        try:
            method(self, *args, **kwargs)
        except BaseException:

            test_exc_type, test_exc, test_traceback = sys.exc_info()
            for idx, browser in enumerate(self.browsers):
                try:
                    body = browser.find_element_by_tag_name('body')
                    body_height = body.size['height']
                    window_height = browser.get_window_size()['height']
                    pages = int(math.ceil(float(body_height) / window_height))
                except BaseException:
                    pages = 0

                for i in range(pages):
                    browser.execute_script(
                        'window.scrollTo(0,%s)' % (i*window_height))
                    time.sleep(0.2)
                    browser.get_screenshot_as_file(
                        snapshot_path + "/%s_browser-%s_page-%s.png" % (
                            self.id(),
                            idx,
                            i
                        )
                    )

        finally:
            if 'test_exc' in locals():
                reraise(test_exc_type, test_exc.args[0], tb=test_traceback)

    return wrapper


class BrowserTestCase(unittest.TestCase):
    """Browser test case that can be used with Selenium Webdriver to
    functionally test a website
    """

    def __init__(self, *args, **kwargs):
        self.browsers = list()
        self._driver = None
        self._display = None
        super(BrowserTestCase, self).__init__(*args, **kwargs)

    def start_browser(self, size=FRAME_SIZE, driver="Firefox"):
        """Start and return a Selenium Webdriver browser instance
        """
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

        self._driver = driver()
        self._driver.set_window_size(*size)
        self.browsers.append(self._driver)
        self.addCleanup(self._driver.close)
        return self._driver

    @property
    def browser(self):
        """Returns the last browser started"""
        try:
            return self.browsers[-1]
        except (IndexError, AttributeError):
            raise AttributeError(
                "You need to start a browser before you access it")

    def is_headless(self):
        """Used to determine if the test is running in a headless env"""
        return hasattr(self, "_display")


class HeadlessBrowserTestCase(BrowserTestCase):
    """Seleniun Webdiver test case for headless environemnts

    Browser test case that will start a virtual display to run the
    Webdriver browser in before running test cases
    """

    def start_browser(self, size=FRAME_SIZE, driver="Firefox", **kwargs):
        """Start xvfb headless display and a browser inside it

        Extra keyword args are passed directly to the XvFB interface

        """
        if not hasattr(self, "_display"):
            from pyvirtualdisplay import Display
            self._display = Display(visible=0, size=size, **kwargs)
            self._display.start()

        self.addCleanup(self._display.stop)
        return super(
            HeadlessBrowserTestCase, self).start_browser(
                size=size, driver=driver)
