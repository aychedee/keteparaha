import time
from selenium.common import exceptions


class Page(object):

    def __init__(self, tc, browser=None):
        self.tc = tc
        self.tc.pages.append(self)
        if browser:
            self.browser = browser
        else:
            self.browser = tc.browser

    def click(self, link_text):
        self.browser.find_element_by_link_text(link_text).click()

    def logout(self):
        self.browser.get("/logout")

    def get_via_css(self, selector):
        try:
            return self.browser.find_element_by_css_selector(selector)
        except exceptions.NoSuchElementException:
            raise exceptions.NoSuchElementException(
                'Could not find element identified by css selector: "%s". '
                'in page with text: %s' % (selector, self.body_text()[:1000]))

    def get_all_via_css(self, selector):
        try:
            return self.browser.find_elements_by_css_selector(selector)
        except exceptions.NoSuchElementException:
            raise exceptions.NoSuchElementException(
                'Could not find elements identified by css selector: "%s". '
                'in page with text: %s' % (selector, self.body_text()[:1000]))

    def drop_into_shell(self):
        self.tc.drop_into_shell()

    def body_text(self):
        return self.get_via_css("body").text

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

    def click_button_with_text(self, text):
        for button in self.get_all_via_css("button"):
            if button.text == text and button.is_displayed():
                button.click()
                return
        raise AssertionError(
            "Could not find a button with the text '%s'" % (text,)
        )
