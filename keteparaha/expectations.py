from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException


def _wait_for_condition(
    condition, component, message='', driver=None, timeout=10
):
    """Wait until the expected condition is true and return the result"""
    if not driver:
        driver = component._element
    return WebDriverWait(
        driver, timeout).until(condition, message)


class text_to_be_present_in_component(object):
    """ An expectation for checking if the given text is present in the
    provided component.
    """
    def __init__(self, component, text_):
        self.component = component
        self.text = text_

    def __call__(self, driver):
        return self.text in self.component._element.text


class component_to_be_clickable(object):
    """ An expectation that checks if the given component is clickable """
    def __init__(self, component):
        self.component = component

    def __call__(self, driver):
        try:
            return (
                self.component._element.is_enabled()
                and self.component._element.is_displayed()
            )
        except StaleElementReferenceException:
            return False
