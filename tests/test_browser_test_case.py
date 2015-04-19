from unittest import TestCase
from mock import call, patch, Mock

from keteparaha.browser import (
    BrowserTestCase,
    HeadlessBrowserTestCase,
    snapshot_on_error
)


class SubClassed(BrowserTestCase):

    def do_nothing(self):
        pass


class BrowserTestCaseTest(TestCase):



    def test_browser_returns_last_browser_started(self):

        btc = SubClassed('do_nothing')

        btc.browsers.append('b1')
        btc.browsers.append('b2')
        btc.browsers.append('b3')

        self.assertEqual(btc.browser, 'b3')


@patch('keteparaha.browser.os.makedirs')
class SnapshotOnErrorDecorator(TestCase):

    def test_iterates_over_testcases_browsers(self, mock_makedirs):
        mock_browser = Mock()
        mock_browser.get_window_size.return_value = {
            'height': 100
        }
        mock_browser.find_element_by_tag_name.return_value.size = {
            'height': 340
        }

        def test_func(self, *args, **kwargs):
            raise TypeError()

        class ExampleTest(object):
            browsers = [mock_browser]
            SNAPSHOT_PATH = '/my-path'

            def id(self):
                return 'test-id'

        decorated = snapshot_on_error(test_func)

        with self.assertRaises(TypeError):
            decorated(ExampleTest())

        self.assertEqual(
            mock_makedirs.call_args, call(ExampleTest.SNAPSHOT_PATH))
        self.assertEqual(
            mock_browser.find_element_by_tag_name.call_args, call('body'))
        self.assertEqual(
            mock_browser.execute_script.call_args_list,
            [
                call('window.scrollTo(0,0)'),
                call('window.scrollTo(0,100)'),
                call('window.scrollTo(0,200)'),
                call('window.scrollTo(0,300)')
            ]
        )
        self.assertEqual(
            mock_browser.get_screenshot_as_file.call_args_list,
            [
                call('/my-path/test-id_browser-0_page-0.png'),
                call('/my-path/test-id_browser-0_page-1.png'),
                call('/my-path/test-id_browser-0_page-2.png'),
                call('/my-path/test-id_browser-0_page-3.png')
            ]
        )

    def test_handles_errors_figuring_out_window_size(self, mock_makedirs):
        mock_browser = Mock()
        mock_browser.find_element_by_tag_name.side_effect = KeyError

        def test_func(self, *args, **kwargs):
            raise TypeError('a type error')

        class ExampleTest(object):
            browsers = [mock_browser]
            SNAPSHOT_PATH = '/my-path'

            def id(self):
                return 'test-id'

        decorated = snapshot_on_error(test_func)

        with self.assertRaises(TypeError):
            decorated(ExampleTest())

        self.assertEqual(
            mock_makedirs.call_args, call(ExampleTest.SNAPSHOT_PATH))
        self.assertEqual(
            mock_browser.find_element_by_tag_name.call_args, call('body'))
        self.assertEqual(mock_browser.execute_script.call_args_list, [])
        self.assertEqual(
            mock_browser.get_screenshot_as_file.call_args_list, [])



@patch('keteparaha.browser.webdriver')
class HeadlessBrowserTestCaseTest(TestCase):

    def test_start_browser(self, mock_webdriver):

        class SampleTC(HeadlessBrowserTestCase):
            _display = Mock()

            def runTest(self):
                pass

        tc = SampleTC()

        tc.start_browser()

        self.assertEqual(tc._driver, mock_webdriver.Firefox.return_value)
