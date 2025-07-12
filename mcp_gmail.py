import os
from mcp.server.fastmcp import FastMCP
from Tools.Google.gmail_tools import GmailTool, EmailMessage, EmailMessages, Labels

working_dir = os.path.dirname(__file__)
gmail_tool = GmailTool(os.path.join(working_dir, 'credentials.json'))

mcp = FastMCP(
    'Gmail',
    dependencies = [
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib'
    ]
)



@mcp.tool()
def send_email(to: str, subject: str, message_text: str, files: list[str] = None) -> dict:
    """Sends an email to the specified recipient.

    Args:
        to: The recipient's email address.
        subject: The subject of the email.
        message_text: The body of the email.
        files: A list of file paths to attach to the email.

    Returns:
        A dictionary containing the sent message's ID and thread ID.
    """
    return gmail_tool.send_email(to, subject, message_text, files)

@mcp.tool()
def search_emails(query: str, max_results: int = 10) -> dict:
    """Searches for emails matching the given query.

    Args:
        query: The query to search for.
        max_results: The maximum number of results to return.

    Returns:
        A list of email messages matching the query.
    """
    return gmail_tool.search_emails(query, max_results).model_dump()

@mcp.tool()
def get_email(msg_id: str) -> dict:
    """Gets the details of a specific email message.

    Args:
        msg_id: The ID of the email message to retrieve.

    Returns:
        An EmailMessage object containing the email's details.
    """
    return gmail_tool.get_email(msg_id).model_dump()

@mcp.tool()
def delete_email(msg_id: str) -> None:
    """Deletes an email message by moving it to the trash.

    Args:
        msg_id: The ID of the email message to delete.
    """
    return gmail_tool.delete_email(msg_id)

@mcp.tool()
def list_labels() -> dict:
    """Lists all the labels in the user's mailbox.

    Returns:
        A list of labels.
    """
    return gmail_tool.list_labels().model_dump()


    
if __name__ == "__main__":
    # default transport == "stdio"
    mcp.run(transport="stdio")          # or mcp.run(transport="stdio")