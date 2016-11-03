from mock import Mock
from unittest import TestCase
from selenium.webdriver.remote.webdriver import WebDriver

from keteparaha.page import Component, Page


class HomePage(Page):
    url = 'https://obviously-not-real.com/'

    def get_elements(self, selector):
        return [i for i in range(10)]


class CoolPage(Page):
    url = 'https://obviously-not-real.com/path'

    def setup(self, _query):
        self.query = _query


class ComplexPathPage(Page):
    url = r'/s/([0-9]{4})/(?P<slug>[\w]+)/$'

    def setup(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Modal(Component):
    selector = '#modal-id'

    def __repr__(self):
        return super(Modal, self).__repr__()

    @property
    def _element(self):
        return MockDriver()


class ModalNext(Component):
    selector = '#modal-next'

    def __repr__(self):
        return super(Modal, self).__repr__()


class MockDriver(WebDriver):

    current_url = ''
    session_id = ''

    def __init__(self):
        self.current_url = ''

    @property
    def _element(self):
        return MockDriver()

    def is_enabled(self):
        return True

    def is_displayed(self):
        return True

    def find_element_by_css_selector(self, selector):
        return Mock()

    def find_element_by_link_text(self, selector):
        return Mock()

    def find_elements_by_tag_name(self, selector):
        return [
            type('btn', (Mock,), {'_parent': MockDriver()})(text=t)
                for t in  ['yes', 'no', 'button text']]

    def get(self, url):
        self.current_url = url

    def find_element(self, *args):
        return self

    def find_elements(self, *args):
        return [i for i in range(10)]

    def click(self):
        pass

    def send_keys(*text):
        raise Exception('Send keys called with {}'.format(text))


class MockParent(object):
    _driver = ''


class PageTest(TestCase):

    def test_dynamically_switches_page_class_based_on_url(self):
        home = HomePage(driver=MockDriver())
        home._driver.current_url = CoolPage.url + '?search=hello'
        cool_page = home.click('.btn')

        self.assertIsInstance(cool_page, CoolPage)
        self.assertEqual(cool_page.query, {'search': ['hello']})

    def test_dynamically_passes_captured_url_elements_to_component(self):
        home = HomePage(driver=MockDriver())
        home._driver.current_url = ComplexPathPage.url.replace(
            '([0-9]{4})', '9999').replace(
            '(?P<slug>[\w]+)/$', 'thisisthearticle/'
        ) + '?hello=world&testers=are_people#fragment'
        complex_page = home.click('.btn')

        self.assertIsInstance(complex_page, ComplexPathPage)
        self.assertEqual(complex_page.args, ('9999',))
        self.assertEqual(complex_page.kwargs['slug'], 'thisisthearticle')
        self.assertEqual(
            complex_page.kwargs['_query'],
            {'hello': ['world'], 'testers': ['are_people']}
        )
        self.assertEqual(complex_page.kwargs['_fragment'], 'fragment')

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

        for idx, row in enumerate(rows):
            self.assertEqual(row._find_by, 'index_position')
            self.assertEqual(row._index_position, idx)

    def test_repr_of_dynamic_components(self):
        home = HomePage(driver=MockDriver())
        rows = home.get_components('tr')

        self.assertEqual(
            str(rows[0]), 'DynamicComponent(selector="tr")[0]')

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

    def test_enter_text_calls_elements_send_keys_method(self):
        home = HomePage(driver=MockDriver())
        modal = home.get_component('#modal-id')

        with self.assertRaises(Exception) as exc:
            modal.enter_text('selector', 'test text')

        self.assertIn("'t', 'e', 's', 't'", exc.exception.args[0], '')
