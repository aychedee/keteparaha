"""Page class, intended to be sub classed as an abstraction for a real web page

Page classes collect the logic for how to use a certain part of the web site
under test into one area.

"""
import time
from selenium.common import exceptions


class Page(object):
    """Generic web page, intended to be subclassed

    class LoginPage(Page):

        def login(username, password):
            self.browser.get("/login")
            self.get_all_via_css("input[name=username]").send_keys(username)
            self.get_all_via_css("input[name=password]").send_keys(password)
            self.get_all_via_css("input[type=submit]").click()
            return Dashboard(self.tc)
    """

    def __init__(self, tc, browser=None):
        self.tc = tc
        self.tc.pages.append(self)
        if browser:
            self.browser = browser
        else:
            self.browser = tc.browser

    def click(self, link_text):
        """Convenience method for clicking links"""
        self.browser.find_element_by_link_text(link_text).click()

    def get_via_css(self, selector):
        """Shortand for getting html elements via css selectors"""
        try:
            return self.browser.find_element_by_css_selector(selector)
        except exceptions.NoSuchElementException:
            raise exceptions.NoSuchElementException(
                'Could not find element identified by css selector: "%s". '
                'in page with text: %s' % (selector, self.body_text()[:1000]))

    def get_all_via_css(self, selector):
        """Shortand for getting a list of html elements via css selectors"""
        try:
            return self.browser.find_elements_by_css_selector(selector)
        except exceptions.NoSuchElementException:
            raise exceptions.NoSuchElementException(
                'Could not find elements identified by css selector: "%s". '
                'in page with text: %s' % (selector, self.body_text()[:1000]))

    def drop_into_shell(self):
        """Drop into an IPython shell at the point this method is called

        Useful for interactive debugging. Inside the shell self is the
        test case and all created page objects will be available in
        self.pages.

        """
        self.tc.drop_into_shell()

    def body_text(self):
        """Get body text for current page"""
        return self.get_via_css("body").text

    def wait_for_visibility(self, selector, timeout_seconds=20):
        """Waits for an element to be displayed and returns it

        Raises an ElementNotVisibleException if the element does not become
        visible or doesn't exist after the timeout.
        """
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

    def wait_for_invisibility(self, selector, timeout_seconds=20):
        """Waits for an element to not be displayed or not exist

        Raises an InvalidElementStateException if the element does not become
        invisible or exists after the timeout.
        """
        pause_interval = 1
        retries = timeout_seconds / pause_interval
        while retries:
            try:
                element = self.get_via_css(selector)
                if not element.is_displayed():
                    return element
            except (exceptions.NoSuchElementException,
                    exceptions.StaleElementReferenceException):
                return None

            retries = retries - pause_interval
            time.sleep(pause_interval)
        raise exceptions.InvalidElementStateException(
            "Element %s is visible despite waiting for %s seconds" % (
                selector, timeout_seconds)
        )

    def click_button_with_text(self, text):
        """Find buttons on the page and click the first one with the text"""
        for button in self.get_all_via_css("button"):
            if button.text == text and button.is_displayed():
                button.click()
                return
        raise AssertionError(
            "Could not find a button with the text '%s'" % (text,)
        )
