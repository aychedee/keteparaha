# -*- coding: utf-8 -*-
"""Gmail IMAP client for testing automated emails

Example:

    gmail = GmailImapClient('testing+566b@domain.com', 'xxxxx')
    msgs = gmail.gmail_search('from:info@time.com is:unread')

"""
from datetime import datetime, timedelta
import email
from imapclient import IMAPClient


def email_bodies(emails):
    """Return a list of email text bodies from a list of email objects"""
    body_texts = []
    for eml in emails:
        body_texts.extend(list(eml.walk())[1:])
    return body_texts


class GmailImapClient(object):
    """Imap client with some specific methods for working with gmail"""

    IMAP_SERVER = "imap.gmail.com"
    IMAP_SERVER_PORT = "993"

    def __init__(self, email_address, password):
        self.client = IMAPClient(self.IMAP_SERVER, use_uid=True, ssl=True)
        self.email_address = email_address
        self.password = password
        self.messages_for_this_session = []
        self._login()

    def search(self, from_address, to_address, subject,
               since=datetime.utcnow()-timedelta(minutes=1)):
        """Search for emails on an IMAP server"""

        return self.emails_from_messages(
            self.client.search(
                [
                    'FROM "%s"' % (from_address,),
                    'TO "%s"' % (to_address,),
                    'SUBJECT "%s"' % (subject,),
                    'SINCE %s' % (since.strftime('%d-%b-%Y'),),
                ],
            )
        )

    def _login(self):
        """Login to imap server"""
        self.client.login(self.email_address, self.password)
        self.client.select_folder("INBOX")

    def delete_seen_messages(self):
        """Delete messages that have been accessed with this client"""
        self.client.delete_messages(self.messages_for_this_session)
        self.client.expunge()

    def gmail_search(self, query):
        """Search the gmail imap server using gmail queries"""
        self.client.logout()
        self.client = IMAPClient(self.IMAP_SERVER, use_uid=True, ssl=True)
        self._login()
        # Can use full gmail queries like 'has:attachment in:unread'
        messages = self.client.gmail_search(query)
        self.messages_for_this_session.append(messages)
        # We recreate a whole connection after querying gmail because
        # otherwise it caches our search results forever
        self.client.logout()
        self.client = IMAPClient(self.IMAP_SERVER, use_uid=True, ssl=True)
        self._login()
        return self.emails_from_messages(messages)

    def emails_from_messages(self, messages):
        """Convert a list of IMAP messages into email objects"""
        response = self.client.fetch(messages, ["RFC822"])
        return [
            email.message_from_string(data["RFC822"])
            for _, data in response.iteritems()
        ]
