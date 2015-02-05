from datetime import datetime, timedelta
import email
from imapclient import IMAPClient


class GmailImapClient(object):

    IMAP_SERVER = "imap.gmail.com"
    IMAP_SERVER_PORT = "993"

    def __init__(self, email_address, password):
        self.client = IMAPClient(self.IMAP_SERVER, use_uid=True, ssl=True)
        self.email_address = email_address
        self.password = password
        self.messages_for_this_session = []
        self.login()

    def search(self, from_address, to_address, subject, search_criteria,
               since=datetime.utcnow()-timedelta(minutes=1)):

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

    def login(self):
        self.client.login(self.email_address, self.password)
        self.client.select_folder("INBOX")

    def delete_messages_seen_in_this_session(self):
        self.client.delete_messages(self.messages_for_this_session)
        self.client.expunge()

    def gmail_search(self, query):
        self.client.logout()
        self.client = IMAPClient(self.IMAP_SERVER, use_uid=True, ssl=True)
        self.login()
        # Can use full gmail queries like 'has:attachment in:unread'
        messages = self.client.gmail_search(query)
        self.messages_for_this_session.append(messages)
        # We recreate a whole connection after querying gmail because
        # otherwise it caches our search results forever
        self.client.logout()
        self.client = IMAPClient(self.IMAP_SERVER, use_uid=True, ssl=True)
        self.login()
        return self.emails_from_messages(messages)

    def emails_from_messages(self, messages):
        response = self.client.fetch(messages, ["RFC822"])
        return [
            email.message_from_string(data["RFC822"])
            for msgid, data in response.iteritems()
        ]

    def email_bodies(self, emails):
        email_bodies = []
        for email in emails:
            email_bodies.extend(list(email.walk())[1:])
        return email_bodies
