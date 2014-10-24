from selenium import webdriver
from selenium.common import exceptions
import time
import unittest


class BrowserTestCase(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        super(BrowserTestCase, self).setUp(*args, **kwargs)
        try:
            driver = getattr(webdriver, kwargs.get("driver", "Firefox"))
        except AttributeError:
            supported_drivers = [
                d for d in webdriver.__dict__.keys()
                    if d[0].isupper() and d not in [
                        'ActionChains', 'FirefoxProfile',
                        'ChromeOptions', 'TouchActions',
                        'DesiredCapabilities'
                    ]
            ]
            raise Exception(
                "No such driver. Choose from." % (supported_drivers,))

        self.browser = driver()

    def tearDown(self, *args, **kwargs):
        super(BrowserTestCase, self).tearDown(*args, **kwargs)
        self.browser.close()

    def wait_for_visibility(self, selector, timeout_seconds=20):
        pause_interval = 1
        retries = timeout_seconds / pause_interval
        while retries:
            try:
                element = self.get_via_css(selector)
                if element.is_displayed():
                    return element
            except (exceptions.NoSuchElementException,
                    exceptions.StaleElementReferenceException):
                if retries <= 0:
                    raise
                else:
                    pass

            retries = retries - pause_interval
            time.sleep(pause_interval)
        raise exceptions.ElementNotVisibleException(
            "Element %s not visible despite waiting for %s seconds" % (
                selector, timeout_seconds)
        )

    def body_text(self):
        return self.browser.find_element_by_css_selector("body").text

    def get_via_css(self, selector):
        try:
            return self.browser.find_element_by_css_selector(selector)
        except exceptions.NoSuchElementException:
            raise exceptions.NoSuchElementException(
                'Could not find element identified by css selector: "%s". '
                'in page with text: %s' % (selector, self.body_text()[:1000])
            )

