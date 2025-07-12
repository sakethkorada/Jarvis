
import unittest
import os
from unittest.mock import patch, MagicMock
from Tools.Google.gmail_tools import GmailTool, EmailMessage, EmailMessages, Labels

class TestMCPGmail(unittest.TestCase):

    @patch('Tools.Google.gmail_tools.GmailTool')
    def test_send_email(self, MockGmailTool):
        mock_gmail_tool = MockGmailTool.return_value
        mock_gmail_tool.send_email.return_value = {'id': '123', 'threadId': '456'}

        from mcp_gmail import send_email
        result = send_email('test@example.com', 'Test Subject', 'Test Body')

        self.assertEqual(result, {'id': '123', 'threadId': '456'})
        mock_gmail_tool.send_email.assert_called_once_with('test@example.com', 'Test Subject', 'Test Body', None)

    @patch('Tools.Google.gmail_tools.GmailTool')
    def test_search_emails(self, MockGmailTool):
        mock_gmail_tool = MockGmailTool.return_value
        mock_gmail_tool.search_emails.return_value = EmailMessages(messages=[EmailMessage(id='123', threadId='456', labelIds=['INBOX'], snippet='Test Snippet', payload=None)], resultSizeEstimate=1)

        from mcp_gmail import search_emails
        result = search_emails('test query')

        self.assertEqual(len(result.messages), 1)
        self.assertEqual(result.messages[0].id, '123')
        mock_gmail_tool.search_emails.assert_called_once_with('test query', 10)

    @patch('Tools.Google.gmail_tools.GmailTool')
    def test_get_email(self, MockGmailTool):
        mock_gmail_tool = MockGmailTool.return_value
        mock_gmail_tool.get_email.return_value = EmailMessage(id='123', threadId='456', labelIds=['INBOX'], snippet='Test Snippet', payload=None)

        from mcp_gmail import get_email
        result = get_email('123')

        self.assertEqual(result.id, '123')
        mock_gmail_tool.get_email.assert_called_once_with('123')

    @patch('Tools.Google.gmail_tools.GmailTool')
    def test_delete_email(self, MockGmailTool):
        mock_gmail_tool = MockGmailTool.return_value
        mock_gmail_tool.delete_email.return_value = None

        from mcp_gmail import delete_email
        delete_email('123')

        mock_gmail_tool.delete_email.assert_called_once_with('123')

    @patch('Tools.Google.gmail_tools.GmailTool')
    def test_list_labels(self, MockGmailTool):
        mock_gmail_tool = MockGmailTool.return_value
        mock_gmail_tool.list_labels.return_value = Labels(labels=[{'id': 'INBOX', 'name': 'INBOX', 'messageListVisibility': 'show', 'labelListVisibility': 'labelShow', 'type': 'system'}])

        from mcp_gmail import list_labels
        result = list_labels()

        self.assertEqual(len(result.labels), 1)
        self.assertEqual(result.labels[0]['id'], 'INBOX')
        mock_gmail_tool.list_labels.assert_called_once()

if __name__ == '__main__':
    unittest.main()
