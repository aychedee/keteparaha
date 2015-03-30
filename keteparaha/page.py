# -*- coding: utf-8 -*-
"""Page and page Component classes

The keteparaha Page and Component classes represent web pages and components
of web pages.

Pages are identified by the URL of the browser, and components by the CSS
selector that is used to retrieve them.

If you perform an action that causes the browser to visit a new URL, and
you have defined a Page class with that URL, then the new page will
automatically be returned from that action.

Creating an instance of a page object will automatically cause the browser to
visit that page as well.

Example:
    BASE_URL = 'http://my-site.com'

    class Home(Page):
        url = BASE_URL + '/'

    class Dashboard(Page):
        url = BASE_URL + '/dashboard/'

    class

    home = Home(driver)  # driver is a WebDriver instance, browser would
                         # automatically visit the home page at this point

    dashboard = home.click_link('Dashboard')

"""
from __future__ import unicode_literals
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
from six import with_metaclass

from .expectations import (
    _wait_for_condition,
    component_to_be_clickable,
    text_to_be_present_in_component
)

ELEMENT_TIMEOUT = 10
""" (int): The seconds that a component will wait to be visible, clickable, or
    present before raising a TimeoutException
"""

__all__ = ['Component', 'Page']


# Workaround for backwards compatibility with Python 2.7
try:
    unicode = unicode
except NameError:
    basestring = (str, bytes)


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
        try:
            return type(
                'DynamicComponent', (Component,), {'selector': selector})
        except TypeError:  # Python < 3
            return type(
                b'DynamicComponent', (Component,), {'selector': selector})
            return


class _RegistryMeta(type):
    """Add our pages and components to a central registry"""

    def __init__(cls, name, bases, dct):
        if dct.get('url'):
            cls._registry[dct.get('url')] = cls
        elif dct.get('selector'):
            cls._registry[dct.get('selector')] = cls

        return super(_RegistryMeta, cls).__init__(name, bases, dct)


class _SeleniumWrapper(object):
    """Mixin for page and component class that understands the WebDriver API
    """

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
                '"{0}" could not be found in page'.format(
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

        for idx, element in enumerate(elements):
            comp_inst = self._get_component_class(
                component_or_selector)(self, find_by='index_position')
            comp_inst._index_position = idx
            components.append(comp_inst)

        return components

    def get_element(self, selector, driver=None):
        """Get the DOM element identified by the css selector"""
        return _wait_for_condition(
            ec.presence_of_element_located((By.CSS_SELECTOR, selector)),
            self,
            message='No element found with selector "{0}".'.format(selector),
            driver=driver
        )

    def get_clickable_element(self, selector, driver=None):
        """Return an element that can be clicked, or raise an error"""
        return _wait_for_condition(
            ec.element_to_be_clickable((By.CSS_SELECTOR, selector)),
            self,
            message='No clickable element found with selector "{0}".'.format(
                selector),
            driver=driver
        )

    def get_visible_element(self, selector):
        """Return an element that is visible, or raise an error"""
        return _wait_for_condition(
            ec.visibility_of_element_located((By.CSS_SELECTOR, selector)),
            self,
            message='No visible element found with selector "{0}".'.format(
                selector)
        )

    def get_element_by_link_text(self, link_text):
        """Get the DOM element identified by the css selector"""
        return _wait_for_condition(
            ec.presence_of_element_located((By.LINK_TEXT, link_text)),
            self,
            message='No link with text "{0}".'.format(link_text)
        )

    def get_elements(self, selector):
        """Get a list of elements identified by the css selector"""
        return _wait_for_condition(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, selector)),
            self
        )

    def get_attribute(self, attribute):
        """Return the value of an attribute of the component"""
        return self._element.get_attribute(attribute)

    def wait_for_invisibility(self, selector):
        """Pause until the element identified by selector is invisible"""
        return _wait_for_condition(
            ec.invisibility_of_element_located((By.CSS_SELECTOR, selector)),
            self
        )

    def text_in_element(self, selector, text):
        """Return whether the text is in the element identified by selector"""
        return _wait_for_condition(
            ec.text_to_be_present_in_element(
                (By.CSS_SELECTOR, selector), text),
            self,
            message='"{0}" not found in "{1}".'.format(
                text, self.get_component(selector).text)
        )

    def has_text(self, text):
        """Return whether the text is in the component"""
        return _wait_for_condition(
            text_to_be_present_in_component(self, text),
            self,
            message='"{0}" not found in "{1}".'.format(
                text, self._element.text)
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
            message='"{0}" was never clickable'.format(self)
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
            'selector, "{0}", not a string or Component instance.'.format(
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

    def location(self):
        """The current page location without any query parameters"""
        return self.page._driver.current_url.split('?')[0]

    def select_option(self, selector, option_text):
        """Select option in dropdown identified by selector with given text"""
        Select(self.get_element(selector)).select_by_visible_text(option_text)

    def scroll_into_view(self):
        """Scroll the window until the component is visible"""
        self._element.location_once_scrolled_into_view

    def clear(self, selector):
        """Clear text out of input identified by CSS selector"""
        try:
            self.get_visible_element(selector).clear()
        except (exceptions.InvalidElementStateException,
                exceptions.WebDriverException):
            raise exceptions.WebDriverException(
                'You cannot clear that element')

    def hover(self, selector, opens=None):
        """Hover over element identified by CSS selector"""
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
        raise AssertionError("Unable to correctly type {0}".format(text))


class _WebElementProxy(object):
    """A proxy to the Selenium WebElement identified by obj's selector"""
    def __init__(self):
        self.selector = 'html'

    def __get__(self, obj, owner):
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
                    'No element "{0}", waited {1} seconds'.format(
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
            try:
                return obj._driver.find_element_by_link_text(selector)
            except exceptions.NoSuchElementException:
                return WebDriverWait(obj._driver, ELEMENT_TIMEOUT).until(
                    ec.presence_of_element_located(
                        (
                            By.LINK_TEXT,
                            selector
                        )
                    ),
                    'No link with text "{0}", waited {1} seconds'.format(
                        selector, ELEMENT_TIMEOUT
                    )
                )

        elif obj._find_by == 'index_position':
            idx = obj._index_position
            return obj._driver.find_elements_by_css_selector(selector)[idx]

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
        """The visible text of the component"""
        return self._element.text


class Component(
    with_metaclass(_RegistryMeta, _BaseComponent, _SeleniumWrapper)):
    """Generic page component, intended to be subclassed

    Pages and Components are stored in a registry and switched to dynamically

    class ShoppingBasket(Component):
        selector = '#shopping-basket'

        def remove_item(self, name):
            contents = self.get_components('tr')
            for item in contents:
                if name in item.text:
                    item.click('.remove')
                    return
            raise AssertionError('No item in basket called "{0}"'.format(name))

    page = Page(driver)
    basket = page.click_link('Shopping Basket', opens=ShoppingBasket)
    # The following would also work identically:
    ## basket = page.click_link('Shopping Basket', opens='#shopping-basket')

    basket.remove_item('Buzz Lightyear')

    """

    _registry = _Registry()
    selector = None

    def __repr__(self):
        output = '{0}(selector="{1}")'.format(
            self.__class__.__name__, self.selector)
        if self._find_by == 'index_position':
            output = output + '[{0}]'.format(self._index_position)
        return output

    def __init__(self, parent, driver=None, find_by='selector'):
        self._parent = parent
        self._find_by = find_by

    @property
    def _driver(self):
        return self._parent._element

    @property
    def page(self):
        if isinstance(self._parent, Page):
            return self._parent
        return self._parent.page

    @property
    def url(self):
        """The url of the page which the component is inside"""
        return self.page.url


class Page(
    with_metaclass(_RegistryMeta, _BaseComponent, _SeleniumWrapper)):
    """Generic web page, intended to be subclassed

    Pages and Components are stored in a registry and switched to dynamically

    class LoginPage(Page):
        url = 'https://your-site.com/login

        def login(username, password):
            self.enter_text("input[name=username]", username)
            self.enter_text("input[name=password]", password)
            return self.click("input[type=submit]")
    """
    _driver = WebDriverOnly()
    _registry = _Registry()

    def __init__(self, driver=None):
        self._find_by = 'selector'
        self.selector = 'html'
        try:
            self._driver = driver
        except TypeError:   # Driver was a WebElement, not WebDriver
            self._driver = driver.parent
        if self.location() != self.url:
            self._driver.get(self.url)

    @property
    def page(self):
        """Unifies the api for pages and components slightly"""
        return self
