from unittest import TestCase

from keteparaha.browser import BrowserTestCase


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

