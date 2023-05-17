# sourcery skip: hoist-statement-from-loop, swap-if-else-branches, use-named-expression
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import email
import pandas
from bs4 import BeautifulSoup
import base64

# Define the scopes for the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Create the flow object to get the authorization URL
flow = InstalledAppFlow.from_client_secrets_file(
    'EmailExtract\secret.json', SCOPES)
creds = flow.run_local_server(port=0)

# Create the Gmail API client object
mailSvc = build('gmail', 'v1', credentials=creds)

# Search for all unread emails with the specified label
results = mailSvc.users().messages().list(userId='me', q='label:extraction').execute()
messages = results.get('messages', [])

for _ in messages:
    msg = mailSvc.users().messages().get(userId='me', id=_['id']).execute()
    headers = msg['payload']['headers']
    sender = ""
    date = ""
    subject = ""
    body = ""
    subject = [header['value'] for header in headers if header['name'] == 'Subject'][0]
    date = [header['value'] for header in headers if header['name'] == 'Date'][0]
    sender = [header['value'] for header in headers if header['name'] == 'From'][0]
    
    for _ in msg['payload']['parts']:
        if _["mimeType"] in ["text/plain", "text/html"]:
            content = base64.urlsafe_b64decode(_["body"]["data"]).decode("utf-8")
            
            soup = BeautifulSoup(content, 'html.parser')
            print(soup)
            