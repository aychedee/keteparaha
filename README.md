Keteparaha
==========

[![Join the chat at https://gitter.im/aychedee/keteparaha](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/aychedee/keteparaha?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![PyPI version](https://badge.fury.io/py/keteparaha.svg)](http://badge.fury.io/py/keteparaha) [![Build Status](https://travis-ci.org/aychedee/keteparaha.svg)](https://travis-ci.org/aychedee/keteparaha) [![Coverage Status](https://coveralls.io/repos/aychedee/keteparaha/badge.svg?branch=master)](https://coveralls.io/r/aychedee/keteparaha?branch=master)

Keteparaha is a collection of tools to help when functional testing

It contains utilities that assist with tasks like running a browser in a
headless environment, or checking that emails have been sent, or a file has
been uploaded to a server, or common testing flow control like retrying or
ignoring certain errors.

:copyright: (c) 2015 by Hansel Dunlop.

:license: GPLv3, see LICENSE for more details


BrowserTestCase
---------------

A browser test case for testing web applications. Subclass it and call the
`start_browser` method with the name of the browser you want to test with.
Closing the browser is handled automatically. For example:

    from test_helpers import BrowserTestCase


    class YourTestCase(BrowserTestCase):

        def setUp(self):
            self.browser = self.start_browser("Firefox")

        def test_page_loads(self):
            self.browser.get('127.0.0.1:8080')

            self.assertIn("Hello, World", self.body_text)


HeadlessBrowserTestCase
-----------------------

Requires XvFB to be installed (`sudo apt-get install xvfb`).

Designed for testing web applications on a headless server, probably running
as part of continuous integration. Usage is exactly like the BrowserTestCase
except that you won't see a browser window open, everything should be done
inside a virtual display.

The example below would run Firefox inside a virtual display with a width of
1200px and height of 900px.

    from test_helpers import HeadlessBrowserTestCase


    class YourTestCase(HeadlessBrowserTestCase):

        def setUp(self):
            self.browser = self.start_browser("Firefox", size=(1200, 900))

Remaining keyword arguments to start browser will be passed down to the
virtual display driver. But the other defaults are generally sensible.

Page
----

The Page class represents a page in your application and should be subclassed
and extended. Pages are given urls. Whenever you click a component of your
site and the URL changes the associated page will be returned. Creating an
instance of a class will automatically visit that page.

    from test_helpers import Page
    SERVER_URL = 'http://your-site.com/{}'

    class LoginPage(Page):
        url = SERVER_URL.format('login/')

        def login(self, username, password):
            self.click_button("Login")
            self.enter_text("input[name=username]", username)
            self.enter_text("input[name=password]", password)
            return self.click("input[type=submit]")

    class YourDashboard(Page):
        url = SERVER_URL.format('dashboard/')

        def assert_logged_in(self):
            # Will raise an exception if component not present
            self.get_component(".account-details")


    class YourTestCase(BrowserTestCase):

        def setUp(self):
            self.start_browser()

        def test_login_works(self):
            login_page = LoginPage(driver=self._driver)
            dashboard = login_page.login('username', 'password')

            dashboard.assert_logged_in()

Email
-----

The email module contains a imap client written to interact with gmail. This
is especially useful if you use Google Apps and you're running
tests against it.


Flow Control
------------

This module contains three functions that are intended to make flow control in
testing situations less painful. They can be used as decorators. They are:

* retry
* ignore
* fallback
