

import rpyc

conn = rpyc.connect("localhost", 18861)

def test_send_email():
    to = input("Enter recipient's email: ")
    subject = input("Enter email subject: ")
    message_text = input("Enter email body: ")
    files = input("Enter comma-separated file paths (or leave blank): ")
    files = [f.strip() for f in files.split(',')] if files else None
    result = conn.root.send_email(to, subject, message_text, files)
    print(f"Email sent: {result}")

def test_search_emails():
    query = input("Enter search query: ")
    max_results = int(input("Enter max results (default 10): ") or 10)
    result = conn.root.search_emails(query, max_results)
    print(f"Found {len(result.messages)} emails:")
    for msg in result.messages:
        print(f"  - {msg.id}: {msg.snippet}")

def test_get_email():
    msg_id = input("Enter email ID: ")
    result = conn.root.get_email(msg_id)
    print(f"Email details: {result}")

def test_delete_email():
    msg_id = input("Enter email ID to delete: ")
    conn.root.delete_email(msg_id)
    print(f"Email {msg_id} deleted.")

def test_list_labels():
    result = conn.root.list_labels()
    print("Labels:")
    for label in result.labels:
        print(f"  - {label['name']}")

if __name__ == "__main__":
    while True:
        print("\nChoose a function to test:")
        print("1. Send email")
        print("2. Search emails")
        print("3. Get email")
        print("4. Delete email")
        print("5. List labels")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            test_send_email()
        elif choice == '2':
            test_search_emails()
        elif choice == '3':
            test_get_email()
        elif choice == '4':
            test_delete_email()
        elif choice == '5':
            test_list_labels()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

