import os 
import base64
from typing import Literal, Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pydantic import BaseModel, Field
from .google_apis import create_service

class EmailMessage(BaseModel):
    msg_id: str = Field(..., description="The ID of the email message.")
    subject: str = Field(..., description="The subject of the email message")
    sender: str = Field(..., description="The sender of the email message")
    recipients: str = Field(..., description="The recipients of the email message")
    body: str = Field(..., description="The body of the email message")
    snippet: str = Field(..., description="A snippet of the email message")
    has_attachments: bool = Field(..., description="Indicates if email has attachments")
    date: str = Field(..., description="The date when email was sent")
    star: bool = Field(..., description="Indicates if email is starred")
    label: List[str] = Field(..., description="Labels associated with the email message")

class EmailMessages(BaseModel):
    count: int = Field(..., description="The number of email messages")
    messages: List[EmailMessage] = Field(..., description="List of email messages")
    next_page_token: Optional[str] = Field(..., description="Token for the next page of results.")

class Label(BaseModel):
    id: str = Field(..., description="The ID of the label.")
    name: str = Field(..., description="The display name of the label.")
    message_list_visibility: Optional[str] = Field(None, description="The visibility of messages with this label in the message list.")
    label_list_visibility: Optional[str] = Field(None, description="The visibility of the label in the label list.")
    type: str = Field(..., description="The owner type for the label.")

class Labels(BaseModel):
    labels: List[Label] = Field(..., description="List of labels.")

class GmailTool:
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']

    def __init__(self, client_secret_file: str) -> None:
        self.client_secret_file = client_secret_file
        self._init_service()

    def _init_service(self) -> None:
        self.service = create_service(
            self.client_secret_file,
            self.API_NAME,
            self.API_VERSION,
            self.SCOPES
        )

    def send_email(self, to: str, subject: str, message_text: str, files: List[str] = None) -> dict:
        """Sends an email to the specified recipient.

        Args:
            to: The recipient's email address.
            subject: The subject of the email.
            message_text: The body of the email.
            files: A list of file paths to attach to the email.

        Returns:
            A dictionary containing the sent message's ID and thread ID.
        """
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        message.attach(MIMEText(message_text, 'plain'))

        if files:
            for file_path in files:
                with open(file_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
                message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': raw_message}
        sent_message = self.service.users().messages().send(userId='me', body=create_message).execute()
        return sent_message

    def search_emails(self, query: str, max_results: int = 10) -> EmailMessages:
        """Searches for emails matching the given query.

        Args:
            query: The query to search for.
            max_results: The maximum number of results to return.

        Returns:
            A list of email messages matching the query.
        """
        try:
            response = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = response.get('messages', [])
            email_messages = []
            for msg in messages:
                email_messages.append(self.get_email(msg['id']))
            
            return EmailMessages(
                count=len(email_messages),
                messages=email_messages,
                next_page_token=response.get('nextPageToken')
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return EmailMessages(count=0, messages=[], next_page_token=None)

    def get_email(self, msg_id: str) -> EmailMessage:
        """Gets the details of a specific email message.

        Args:
            msg_id: The ID of the email message to retrieve.

        Returns:
            An EmailMessage object containing the email's details.
        """
        msg = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'] == 'subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'from'), '')
        recipients = next((h['value'] for h in headers if h['name'] == 'to'), '')
        date = next((h['value'] for h in headers if h['name'] == 'date'), '')
        
        body, has_attachments = self._get_body_content(payload)
        
        return EmailMessage(
            msg_id=msg['id'],
            subject=subject,
            sender=sender,
            recipients=recipients,
            body=body,
            snippet=msg.get('snippet', ''),
            has_attachments=has_attachments,
            date=date,
            star='starred' in msg.get('labelIds', []),
            label=msg.get('labelIds', [])
        )

    def _get_body_content(self, payload: dict) -> (str, bool):
        """Extracts the body content and attachment status from an email's payload.

        Args:
            payload: The payload of the email message.

        Returns:
            A tuple containing the email body and a boolean indicating if attachments are present.
        """
        body = ""
        has_attachments = False
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'attachmentId' in part['body']:
                    has_attachments = True
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body, has_attachments

    def delete_email(self, msg_id: str) -> None:
        """Deletes an email message by moving it to the trash.

        Args:
            msg_id: The ID of the email message to delete.
        """
        try:
            self.service.users().messages().trash(userId='me', id=msg_id).execute()
            print(f"Message with id: {msg_id} trashed successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def list_labels(self) -> Labels:
        """Lists all the labels in the user's mailbox.

        Returns:
            A list of labels.
        """
        try:
            response = self.service.users().labels().list(userId='me').execute()
            labels = response.get('labels', [])
            return Labels(labels=labels)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Labels(labels=[])
