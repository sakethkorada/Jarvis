import os
import time

# Import the gmail_tool instance from your main server file
# Make sure your server file is named 'gmail_mcp_server.py' or update the import
from mcp_gmail import gmail_tool

def run_all_tests():
    """
    Executes a series of tests for all Gmail tool methods.
    """
    # --- Configuration ---
    # IMPORTANT: Replace with an email address you can send to and check
    recipient_email = 'recipient@example.com' 
    # A unique subject line to ensure we find the exact test email
    unique_subject = f"MCP Full Tool Test - {int(time.time())}"
    test_msg_id = None

    print("🚀 Starting tests for all Gmail tools...")

    # --- Test 1: list_labels() ---
    print("\n--- 1. Testing list_labels() ---")
    try:
        labels_response = gmail_tool.list_labels()
        if labels_response and labels_response.labels:
            print(f"✅ Success: Found {len(labels_response.labels)} labels.")
            print(f"   Sample labels: {[label.name for label in labels_response.labels[:5]]}")
        else:
            print("⚠️ Warning: No labels found, but the call was successful.")
    except Exception as e:
        print(f"❌ Failure: An error occurred during list_labels(): {e}")
        return # Stop tests if this fails

    # --- Test 2: send_email() ---
    print(f"\n--- 2. Testing send_email() with subject: '{unique_subject}' ---")
    try:
        send_response = gmail_tool.send_email(
            to=recipient_email,
            subject=unique_subject,
            message_text="This is an automated test for the full suite of Gmail tools."
        )
        print(f"✅ Success: Email sent. Message ID: {send_response['id']}")
    except Exception as e:
        print(f"❌ Failure: An error occurred during send_email(): {e}")
        return # Stop if we can't send the email

    # --- Test 3: search_emails() ---
    # Wait a few seconds for Gmail to index the new email
    print("\n(Waiting 5 seconds for email to be indexed...)")
    time.sleep(5) 
    
    print(f"\n--- 3. Testing search_emails() for subject: '{unique_subject}' ---")
    try:
        search_query = f'subject:"{unique_subject}"'
        search_response = gmail_tool.search_emails(query=search_query, max_results=1)
        if search_response and search_response.count > 0:
            test_msg_id = search_response.messages[0].msg_id
            print(f"✅ Success: Found the test email. Message ID: {test_msg_id}")
        else:
            print("❌ Failure: Could not find the test email via search.")
            return
    except Exception as e:
        print(f"❌ Failure: An error occurred during search_emails(): {e}")
        return

    # --- Test 4: get_email() ---
    print(f"\n--- 4. Testing get_email() with ID: {test_msg_id} ---")
    try:
        get_response = gmail_tool.get_email(msg_id=test_msg_id)
        if get_response and get_response.subject == unique_subject:
            print(f"✅ Success: Fetched email details correctly.")
            print(f"   Subject: '{get_response.subject}'")
            print(f"   From: {get_response.sender}")
        else:
            print("❌ Failure: Fetched email does not have the correct subject.")
            return
    except Exception as e:
        print(f"❌ Failure: An error occurred during get_email(): {e}")
        return

    # --- Test 5: delete_email() ---
    print(f"\n--- 5. Testing delete_email() with ID: {test_msg_id} ---")
    try:
        gmail_tool.delete_email(msg_id=test_msg_id)
        # The delete_email function prints its own success message
        print(f"✅ Success: delete_email() executed for message {test_msg_id}.")
    except Exception as e:
        print(f"❌ Failure: An error occurred during delete_email(): {e}")
    
    print("\n🎉 All tests completed.")


if __name__ == "__main__":
    run_all_tests()