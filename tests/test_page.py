from mock import Mock
from unittest import TestCase

from keteparaha.browser import BrowserTestCase
from keteparaha.page import Component, Page


class HomePage(Page):
    url = u'https://obviously-not-real.com/'


class CoolPage(Page):
    url = u'https://obviously-not-real.com/path'


class Modal(Component):
    component_selector = '#modal-id'


class MockDriver(object):

    def __init__(self):
        self.current_url = None

    def find_element_by_css_selector(self, selector):
        return Mock()

    def get(self, url):
        self.current_url = url

    def find_element(self, *args):
        return self

    def click(self):
        pass


class MockTestCase(BrowserTestCase):

    def do_nothing(self):
        pass


class PageTest(TestCase):

    def test_dynamically_switches_page_class_based_on_url(self):
        home = HomePage(MockTestCase('do_nothing'), driver=MockDriver())
        home._driver.current_url = CoolPage.url
        cool_page = home.click('.btn')

        self.assertIsInstance(cool_page, CoolPage)

    def test_dynamically_returns_(self):
        home = HomePage(MockTestCase('do_nothing'), driver=MockDriver())
        home._driver.current_url = CoolPage.url
        modal = home.click('.btn', opens='#modal-id')

        self.assertIsInstance(modal, Modal)
