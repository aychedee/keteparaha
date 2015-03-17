"""Page class, intended to be sub classed as an abstraction for a real web page

Page classes collect the logic for how to use a certain part of the web site
under test into one area.

"""
import collections
from inspect import isclass
import time
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import TimeoutException, WebDriverWait

from .expectations import (
    _wait_for_condition,
    component_to_be_clickable,
    text_to_be_present_in_component
)

ELEMENT_TIMEOUT = 10

__all__ = ['Component', 'Page']


class _Registry(collections.MutableMapping):
    """A singleton registry for pages and components"""
    store = dict()

    def __delitem__(self, key):
        pass

    def __getitem__(self, key):
        return self.store[key]

    def __iter__(self):
        for value in self.store.values():
            yield value

    def __setitem__(self, key, value):
        self.store[key] = value

    def __len__(self):
        return len(self.store)

    def __call__(self, selector):
        try:
            return self.store[selector]
        except KeyError:
            return self.make_class(selector)

    def make_class(self, selector):
        return type('DynamicComponent', (Component,), {'selector': selector})


class _RegistryMeta(type):
    """Add our pages and components to a central registry"""

    def __init__(cls, name, bases, dct):
        cls._registry = _Registry()
        if dct.get('url'):
            cls._registry[dct.get('url')] = cls
        elif dct.get('selector'):
            cls._registry[dct.get('selector')] = cls

        return super(_RegistryMeta, cls).__init__(name, bases, dct)


class _SeleniumWrapper(object):

    TimeoutException = TimeoutException


    class ComponentMissing(Exception):
        pass

    def _get_component_class(self, component_or_selector):
        """Ensure we have a component class

        Either return argument if it's a component, get a registered component,
        or dynamically create a component.

        """
        if isclass(component_or_selector) and issubclass(
                component_or_selector, Component):
            return component_or_selector
        return self._registry(component_or_selector)

    def get_component(self, component_or_selector):
        """Return an initialised component present in page

        takes either a component class to find in the page or a css selector.

        If the selector is not present in the page raises a ComponentMissing
        error.
        """
        ComponentClass = self._get_component_class(component_or_selector)

        try:
            return ComponentClass(self)
        except TimeoutException:
            raise self.ComponentMissing(
                '"{}" could not be found in page'.format(
                    ComponentClass.selector))

    def get_components(self, component_or_selector):
        """Return an list of initialised components present in page

        Returns an empty list if no components could be found
        """
        ComponentClass = self._get_component_class(component_or_selector)

        components = []
        try:
            elements = self.get_elements(ComponentClass.selector)
        except TimeoutException:
            return components

        for idx, element in enumerate(elements, 1):
            individualClass = self._get_component_class(
                    '{}:nth-child({})'.format(component_or_selector, idx))
            components.append(individualClass(self))

        return components

    def get_element(self, selector, driver=None):
        """Get the DOM element identified by the css selector"""
        return _wait_for_condition(
            ec.presence_of_element_located((By.CSS_SELECTOR, selector)),
            self,
            message='No element found with selector "{}".'.format(selector),
            driver=driver
        )

    def get_clickable_element(self, selector, driver=None):
        return _wait_for_condition(
            ec.element_to_be_clickable((By.CSS_SELECTOR, selector)),
            self,
            message='No clickable element found with selector "{}".'.format(
                selector),
            driver=driver
        )

    def get_visible_element(self, selector):
        return _wait_for_condition(
            ec.visibility_of_element_located((By.CSS_SELECTOR, selector)),
            self,
            message='No visible element found with selector "{}".'.format(
                selector)
        )

    def get_element_by_link_text(self, link_text):
        """Get the DOM element identified by the css selector"""
        return _wait_for_condition(
            ec.presence_of_element_located((By.LINK_TEXT, link_text)),
            self,
            message='No link with text "{}".'.format(link_text)
        )

    def get_elements(self, selector):
        """Get a list of elements identified by the css selector"""
        return _wait_for_condition(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, selector)),
            self
        )

    def get_attribute(self, attribute):
        return self._element.get_attribute(attribute)

    def wait_for_invisibility(self, selector):
        return self.assert_element_invisible(selector)

    def text_in_element(self, selector, text):
        return _wait_for_condition(
            ec.text_to_be_present_in_element(
                (By.CSS_SELECTOR, selector), text),
            self,
            message=u'"{}" not found in "{}".'.format(
                text, self.get_component(selector).text)
        )

    def has_text(self, text):
        return _wait_for_condition(
            text_to_be_present_in_component(self, text),
            self,
            message=u'"{}" not found in "{}".'.format(
                text, self._element.text)
        )

    def assert_element_invisible(self, selector):
        return _wait_for_condition(
            ec.invisibility_of_element_located((By.CSS_SELECTOR, selector)),
            self
        )

    def _click(self, component, opens=None):
        """Click an element and return an appropriate component or page

        component -- a keteparaha.page.Component
        opens -- a keteparaha.page.Component to initialise and return
        returns -- either a new Page object if the url changes, the initialised
        Component passed in as opens, or itself
        """

        _wait_for_condition(
            component_to_be_clickable(component), component,
            message='"{}" was never clickable'.format(self)
        )

        component._element.click()
        if opens and isinstance(opens, basestring):
            # open is a string look it up in registry
            return self._registry(opens)(self)
        if opens and issubclass(opens, Component) and isclass(opens):
            # open is an Component class, use it
            return opens(self)
        if opens and isinstance(opens, Component):
            # open is an initialised component, use it
            return opens

        if self.url != self.location() and self.location() in self._registry:
            return self._registry(self.location())(driver=self._driver)
        return self

    def click(self, selector=None, opens=None):
        """Main method for interacting with a page or component

        Returns either self, a new page object based on browser url, or a
        page component based on the selector passed in as 'opens'.
        selector can be a css selector in the form of a string, or a
        selenium WebElement.

        """
        if isinstance(selector, basestring):
            # selector passed in, get component class from registry
            component = self._registry(selector)(self)
            return self._click(component, opens)
        elif isinstance(selector, Component) and isclass(selector):
            # We already have a component class, so just use it
            component = selector(self)
            return self._click(component, opens)
        elif isinstance(selector, Component) and not isclass(selector):
            # We already have an initalised component, so just use it
            component = selector
            return self._click(component, opens)
        elif selector is None:
            # We have no selector so click on yourself
            return self._click(self, opens)

        raise ValueError(
            'selector, "{}", not a string or Component instance.'.format(
                selector))

    def click_link(self, link_text, opens=None):
        component = Component(self, find_by='link_text')
        component.selector = link_text
        return self._click(component, opens)

    def click_button(self, button_text, opens=None):
        """Find buttons on the page and click the first one with the text"""
        component = Component(self, find_by='button_text')
        component.selector = button_text
        return self._click(component, opens)

    def scroll_into_view(self):
        # Accessing this property on an element scrolls it into view
        self._element.location_once_scrolled_into_view

    def _ensure_element(self, selector_or_element):
        if isinstance(selector_or_element, basestring):
            return self.get_element(selector_or_element)
        if isinstance(selector_or_element, Component):
            return self.get_element(selector_or_element.selector)
        if selector_or_element is None:
            # We hit this case when we want to click on the parent component
            return self._element
        return selector_or_element

    def location(self):
        return self.page._driver.current_url.split('?')[0]

    def select_option(self, selector, option_text):
        Select(self.get_element(selector)).select_by_visible_text(option_text)

    def clear(self, selector):
        try:
            self.get_visible_element(selector).clear()
        except (exceptions.InvalidElementStateException,
                exceptions.WebDriverException):
            raise exceptions.WebDriverException(
                'You cannot clear that element')

    def hover(self, selector, opens=None):
        ActionChains(self._driver).move_to_element(
            self.get_element(selector)).perform()
        if opens:
            return self._get_component_class(opens)(self)

    def enter_text(self, selector, text):
        """Enter text into DOM element identified by selector

        The function performs some error checking because as of Jan 2014
        send_keys on the element is unreliable at text entry.

        """
        element = self.get_visible_element(selector)
        for _ in range(5):
            element.send_keys(*text)
            try:
                value_in_place = element.get_attribute("value") or element.text
            except exceptions.StaleElementReferenceException:
                return
            expected = "".join([unicode(v) for v in text])
            if value_in_place == expected:
                return
            try:
                element.clear()
            except (exceptions.InvalidElementStateException,
                    exceptions.WebDriverException):
                return  # Element is not user editable and can't be cleared

            time.sleep(0.2)
        raise AssertionError("Unable to correctly type {}".format(text))


class _WebElementProxy(object):
    """A proxy to the Selenium WebElement identified by obj's selector"""
    def __init__(self):
        self.selector = 'html'

    def __get__(self, obj, owner):
        if obj is None:
            # Geting called as a class method
            raise RuntimeError('Components need to be initialised before use')
        selector = obj.selector if hasattr(obj, 'selector') else self.selector

        if obj._find_by == 'selector':
            try:
                return obj._driver.find_element_by_css_selector(selector)
            except exceptions.NoSuchElementException:
                return WebDriverWait(obj._driver, ELEMENT_TIMEOUT).until(
                    ec.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            selector
                        )
                    ),
                    'Could not find "{}", despite waiting {} seconds'.format(
                        selector, ELEMENT_TIMEOUT
                    )
                )

        elif obj._find_by == 'button_text':
            for button in obj._driver.find_elements_by_tag_name("button"):
                if button.text == obj.selector and button.is_displayed():
                    return button
            raise AssertionError(
                "Could not find a button with the text '%s'" % (selector,)
            )

        elif obj._find_by == 'link_text':
            return obj._driver.find_element_by_link_text(selector)

        else:
            raise ValueError('Element proxy needs to know how to find element')

    def __set__(self, obj, value):
        raise AttributeError()

class WebDriverOnly(object):
    """This attribute must be a WebDriver instance"""
    def __set__(self, obj, value):
        if not isinstance(value, WebDriver):
            raise TypeError('driver must be an instance of WebDriver')
        self.driver = value

    def __get__(self, obj, owner):
        return self.driver


class _BaseComponent(object):
    _element = _WebElementProxy()

    @property
    def text(self):
        return self._element.text


class Component(_BaseComponent, _SeleniumWrapper):
    __metaclass__ = _RegistryMeta
    _driver = WebDriverOnly()

    def __repr__(self):
        return '{}(selector="{}")'.format(
            self.__class__.__name__, self.selector)

    def __init__(self, parent, driver=None, find_by='selector'):
        self._find_by = find_by
        self._parent = parent
        self._driver = parent._driver


    @property
    def page(self):
        if isinstance(self._parent, Page):
            return self._parent
        return self._parent.page

    @property
    def url(self):
        return self.page.url


class Page(_BaseComponent, _SeleniumWrapper):
    """Generic web page, intended to be subclassed

    Pages and Components are stored in a registry and switched to dynamically

    class LoginPage(Page):
        url = 'https://your-site.com/login

        def login(username, password):
            self.enter_text("input[name=username]", username)
            self.enter_text("input[name=password]", password)
            return self.click("input[type=submit]")
    """
    __metaclass__ = _RegistryMeta
    _driver = WebDriverOnly()

    def __init__(self, driver=None):
        self._find_by = 'selector'
        self.selector = 'html'
        self._driver = driver
        if self.location() != self.url:
            self._driver.get(self.url)

    @property
    def page(self):
        """Unifies the api for pages and components slightly"""
        return self
