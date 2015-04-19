# -*- coding: utf-8 -*-
"""A collection of tools to help when functional testing

It contains utilities that assist with tasks like running a browser in a
headless environment, or checking that emails have been sent, or a file has
been uploaded to a server, or common testing flow control like retrying or
ignoring certain errors.

Installation
------------

Keteparaha is available on PyPi. To install the latest release simply run:

    pip install keteparaha

Usage
-----

**BrowserTestCase** is a sub classed unittest.TestCase designed to make
working with Selenium Webdriver simpler. It can operate in headless mode to be
used with continuous integration.

**Page** and **Component** represent a web app's pages, or the components
that can be found on those pages.

    from keteparaha import BrowserTestCase, Component, Page

    SERVER_URL = 'http://www.simple.com/{}'
    # Pages are identified by their full URL with any GET parameters
    # stripped off


    class LoginPage(Page):
        url = SERVER_URL.format('login/')

        def login(self, email, password):
            self.enter_text('input[name=email]', email)
            self.enter_text('input[name=password]', email)
            return self.click('input[name=submut]')


    class Dashboard(Page):
        url = SERVER_URL.format('dashboard/')

        def logged_in_username(self):
            return self.get_component('.username').text

        def open_comment_modal(self, comment):
            return self.click_button('Feedback', opens='#comment')


    class CommentModal(Component)
        selector = '#comment'

        def comment(self, message):
            self.enter_text('input[name=message]', message)
            self.click('input[type=submit]')


    # User logs in and is redirected to the dashboard
    dashboard = LoginPage(self.driver).login('a@b.com', 'xxxxx')

    # Their username is in the top menu
    self.assertEqual(dashboard.logged_in_username(), 'aychedee')

    # They can leave some feedback for the site owner
    comment_modal = dashboard.open_comment_modal()
    comment_modal.comment("Is it tea you're looking for?")

License
-------

Keteparaha is released under the MIT license, see LICENSE in the software
repository for more details. Copyright 2015 by Hansel Dunlop.

"""

__version__ = '0.0.18'
from .email_client import GmailImapClient
from .page import Component, Page
from .browser import (
    BrowserTestCase,
    HeadlessBrowserTestCase,
    snapshot_on_error
)
from .flow import ignore, retry

__all__ = [
    'BrowserTestCase',
    'Component',
    'GmailImapClient',
    'HeadlessBrowserTestCase',
    'ignore',
    'Page',
    'retry',
    'snapshot_on_error'
]
