from mock import Mock
from unittest import TestCase

from keteparaha.browser import BrowserTestCase
from keteparaha.page import Component, Page


class HomePage(Page):
    url = u'https://obviously-not-real.com/'


class CoolPage(Page):
    url = u'https://obviously-not-real.com/path'


class Modal(Component):
    selector = '#modal-id'

    def __repr__(self):
        return super(Modal, self).__repr__()


class MockDriver(object):

    def __init__(self):
        self.current_url = ''

    def find_element_by_css_selector(self, selector):
        return Mock()

    def get(self, url):
        self.current_url = url

    def find_element(self, *args):
        return self

    def find_elements(self, *args):
        return [i for i in range(10)]

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

    def test_dynamically_returns_component(self):
        home = HomePage(MockTestCase('do_nothing'), driver=MockDriver())
        home._driver.current_url = CoolPage.url
        modal = home.click('.btn', opens='#modal-id')

        self.assertIsInstance(modal, Modal)


class ComponentTest(TestCase):

    def test_component_repr(self):
        home = HomePage(MockTestCase('do_nothing'), driver=MockDriver())
        self.assertEqual(repr(Modal(home)), 'Modal(selector="#modal-id")')

    def test_get_component_with_passed_in_component_class(self):
        home = HomePage(MockTestCase('do_nothing'), driver=MockDriver())
        modal = home.get_component(Modal)

        assert isinstance(modal, Component)

    def test_get_component_with_passed_in_component_selector(self):
        home = HomePage(MockTestCase('do_nothing'), driver=MockDriver())
        modal = home.get_component('#modal-id')

        assert isinstance(modal, Component)

    def test_get_component_with_nonexistent_passed_in_component_selector(self):
        home = HomePage(MockTestCase('do_nothing'), driver=MockDriver())
        modal = home.get_component('#modal-id2')

        assert isinstance(modal, Component)

    def test_get_components_gives_unique_selector_to_each_component(self):
        home = HomePage(MockTestCase('do_nothing'), driver=MockDriver())
        rows = home.get_components('tr')

        for idx, row in enumerate(rows, 1):
            self.assertEqual(row.selector, 'tr:nth-child({})'.format(idx))
