from google.oauth2 import service_account
from googleapiclient.discovery import build


# Constants
DOCUMENT_ID = 'YOUR_DOCUMENT_ID'  # Replace with your Google Doc ID

# Load credentials from the JSON file
SCOPES = ['https://www.googleapis.com/auth/documents']
creds = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES
)

# Build the Google Docs service
service = build('docs', 'v1', credentials=creds)


def get_document(document_id):
    """
    Fetches the Google Doc content.
    """
    document = service.documents().get(documentId=document_id).execute()
    return document


def update_google_doc(document_id, requests):
    """
    Sends a batch of requests to update the Google Doc.
    """
    result = service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}
    ).execute()
    return result


def main():
    # Fetch the document to verify access
    doc = get_document(DOCUMENT_ID)
    print(f"Document Title: {doc.get('title')}")

    # Define update requests
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': 'Hello, this is an added sentence at the start of the document.\n'
            }
        },
        {
            'insertText': {
                'location': {
                    'index': 10
                },
                'text': 'Here’s another sentence inserted further down.\n'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': 46
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {
                        'magnitude': 12,
                        'unit': 'PT'
                    },
                    'foregroundColor': {
                        'color': {
                            'rgbColor': {
                                'red': 0.0,
                                'green': 0.0,
                                'blue': 1.0
                            }
                        }
                    }
                },
                'fields': 'bold,foregroundColor,fontSize'
            }
        }
    ]

    # Update the document
    result = update_google_doc(DOCUMENT_ID, requests)
    print(f"Updated document: {result}")


if __name__ == '__main__':
    main()
