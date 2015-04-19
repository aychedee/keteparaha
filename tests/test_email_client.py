from mock import call, patch
from unittest import TestCase

from keteparaha import GmailImapClient


@patch('keteparaha.email_client.IMAPClient')
class GmailClientTest(TestCase):

    def test_init_setups_and_logs_in(self, mock_imap_client):
        client = GmailImapClient('email', 'password')

        self.assertEqual(client.email_address, 'email')
        self.assertEqual(client.password, 'password')
        self.assertEqual(
            mock_imap_client.call_args,
            call(GmailImapClient.IMAP_SERVER, use_uid=True, ssl=True)
        )

        self.assertEqual(
            mock_imap_client().login.call_args,
            call('email', 'password')
        )
        self.assertEqual(
            mock_imap_client().select_folder.call_args,
            call('INBOX')
        )

    @patch('keteparaha.email_client.email.message_from_string')
    def test_gmail_search_performs_login_logout_dance(
        self, mock_message_from_string, mock_imap_client
    ):
        client = GmailImapClient('email', 'password')
        mock_imap_client.return_value.fetch.return_value = {
            1: {'RFC822': 'msg 1'}
        }

        result = client.gmail_search('query')

        self.assertEqual(
            mock_imap_client().logout.call_args_list, [call(), call()])
        self.assertEqual(
            mock_imap_client().login.call_args_list,
            [
                call(client.email_address, client.password),
                call(client.email_address, client.password),
                call(client.email_address, client.password)
            ]
        )
        self.assertEqual(
            mock_imap_client().fetch.call_args_list,
            [
                call(mock_imap_client().gmail_search(), ['RFC822']),
            ]
        )

        self.assertEqual(result, [mock_message_from_string.return_value])

