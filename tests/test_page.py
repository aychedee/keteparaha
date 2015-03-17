from mock import Mock
from unittest import TestCase
from selenium.webdriver.remote.webdriver import WebDriver

from keteparaha.page import Component, Page


class HomePage(Page):
    url = u'https://obviously-not-real.com/'

    def get_elements(self, selector):
        return [i for i in range(10)]


class CoolPage(Page):
    url = u'https://obviously-not-real.com/path'


class Modal(Component):
    selector = '#modal-id'

    def __repr__(self):
        return super(Modal, self).__repr__()

class ModalNext(Component):
    selector = '#modal-next'

    def __repr__(self):
        return super(Modal, self).__repr__()


class MockDriver(WebDriver):

    current_url = ''

    def __init__(self):
        self.current_url = ''

    def find_element_by_css_selector(self, selector):
        return Mock()

    def find_element_by_link_text(self, selector):
        return Mock()

    def find_elements_by_tag_name(self, selector):
        return [
            type('btn', (Mock,), {})(text=t)
                for t in  ['yes', 'no', 'button text']]

    def get(self, url):
        self.current_url = url

    def find_element(self, *args):
        return self

    def find_elements(self, *args):
        return [i for i in range(10)]

    def click(self):
        pass


class MockParent(object):
    _driver = ''


class PageTest(TestCase):

    def test_dynamically_switches_page_class_based_on_url(self):
        home = HomePage(driver=MockDriver())
        home._driver.current_url = CoolPage.url
        cool_page = home.click('.btn')

        self.assertIsInstance(cool_page, CoolPage)

    def test_dynamically_returns_component(self):
        home = HomePage(driver=MockDriver())
        home._driver.current_url = CoolPage.url
        modal = home.click('.btn', opens='#modal-id')

        self.assertIsInstance(modal, Modal)


class ComponentTest(TestCase):

    def test_component_repr(self):
        home = HomePage(driver=MockDriver())
        self.assertEqual(repr(Modal(home)), 'Modal(selector="#modal-id")')

    def test_get_component_with_passed_in_component_class(self):
        home = HomePage(driver=MockDriver())
        modal = home.get_component(Modal)

        self.assertIsInstance(modal, Component)

    def test_get_component_with_passed_in_component_selector(self):
        home = HomePage(driver=MockDriver())
        modal = home.get_component('#modal-id')

        self.assertIsInstance(modal, Component)

    def test_get_component_with_nonexistent_passed_in_component_selector(self):
        home = HomePage(driver=MockDriver())
        modal = home.get_component('#modal-id2')

        self.assertIsInstance(modal, Component)

    def test_get_components_gives_unique_selector_to_each_component(self):
        home = HomePage(driver=MockDriver())
        rows = home.get_components('tr')

        for idx, row in enumerate(rows, 1):
            self.assertEqual(row.selector, 'tr:nth-child({})'.format(idx))


    def test_repr_of_dynamic_components(self):
        home = HomePage(driver=MockDriver())
        rows = home.get_components('tr')

        self.assertEqual(
            str(rows[0]), 'DynamicComponent(selector="tr:nth-child(1)")')

    def test_click_button(self):
        home = HomePage(driver=MockDriver())
        modal = home.get_component('#modal-id')

        modal_next = modal.click_button('button text', opens='#modal-next')

        self.assertIsInstance(modal_next, ModalNext)

    def test_click_link(self):
        home = HomePage(driver=MockDriver())
        modal = home.get_component('#modal-id')

        modal_next = modal.click_link('button text', opens='#modal-next')

        self.assertIsInstance(modal_next, ModalNext)

    def test_click_button_with_passed_in_class(self):
        home = HomePage(driver=MockDriver())
        modal = home.get_component('#modal-id')

        modal_next = modal.click_button('button text', opens=ModalNext)

        self.assertIsInstance(modal_next, ModalNext)

    def test_click_with_passed_in_class(self):
        home = HomePage(driver=MockDriver())
        modal = home.get_component('#modal-id')

        modal_next = modal.click('.btn', opens=ModalNext)

        self.assertIsInstance(modal_next, ModalNext)
