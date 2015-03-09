from unittest import TestCase

from keteparaha.browser import BrowserTestCase


class BrowserTestCaseTest(TestCase):

    class SubClassed(BrowserTestCase):

        def do_nothing(self):
            pass

    def test_start_browser_when_given_unsupported_driver(self):
        bc = self.SubClassed("do_nothing")

        with self.assertRaises(ValueError):
            bc.start_browser(driver="NoReal")

        self.assertEqual(bc._browsers, [])

    def test_browser_is_cleaned_up_afterwards(self):
        bc = self.SubClassed("do_nothing")
        bc.start_browser("Firefox")

        bc.doCleanups()

        with self.assertRaises(Exception):
            bc.title
