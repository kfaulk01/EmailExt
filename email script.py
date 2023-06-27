# sourcery skip: merge-list-append, move-assign-in-block
import os
import base64
import requests
import psycopg2
import re
from tqdm import tqdm
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime

# Gmail API credentials
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
elif not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES)
        creds = flow.run_local_server(port=8080)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
# Set up Gmail API service
mailService = build('gmail', 'v1', credentials=creds)

# Label to search for
label = 'Label_1223118211717221721'

# DB credentials
db_host = '50.87.21.232'
db_port = '5432'
db_name = 'epifinde_EpiBuild'
db_user = 'epifinde_epibuild'
db_pass = 'TFLaoi12@3B'

# Connect to PostgreSQL DB
dbConnect = psycopg2.connect(host=db_host,port=db_port,dbname=db_name,user=db_user,password=db_pass)
cur = dbConnect.cursor()

# Get all messages with the EXTRACTIONS label
try:
    results = mailService.users().messages().list(userId='me', labelIds=[label]).execute()
    messages = results.get('messages', [])
except HttpError as error:
    print(f'An error occurred: {error}')
    messages = []
    
# Display a progress bar and finished message
...
try:
    results = mailService.users().messages().list(userId='me', labelIds=[label]).execute()
    messages = results.get('messages', [])
    print(f"Number of messages: {len(messages)}")    
except HttpError as error:
    print(f"An error occurred: {error}")
    messages = []
    
    
# Loop through messages and extract information
for i, msg in enumerate(tqdm(messages, desc="Extracting data...")):
    for _ in messages:
        msg = mailService.users().messages().get(userId='me', id=msg['id']).execute()
        payload = msg['payload']
        headers = payload['headers']
        
        # Extract information
        for _ in headers:
            if _['name'] == 'From':
                sender = _['value']
            elif _['name'] == 'Subject':
                subject = _['value']
            elif _['name'] == 'Date':
                date = _['value']
        parts = [payload]
        data=''
        for _ in parts:
            if _['mimeType'] == 'text/plain':
               # Start after the ---------- Forwarded message --------- line 
                body_text = base64.urlsafe_b64decode(_['body']['data']).decode('utf-8')
                start_index = body_text.find("---------- Forwarded message ---------")
                if start_index != -1:
                    data = base64.urlsafe_b64decode(_['body']['data'][start_index + len("---------- Forwarded message ---------"):]).decode('utf-8')
            elif _['mimeType'] == 'text/html':
                html = base64.urlsafe_b64decode(_['body'][data]).decode('utf-8')
                urls = re.findall(r'(https?://[^\\s@]+)', html)
                for url in urls:
                    links = []
                    r = requests.get(_)
                    title = re.findall('<title>(.*?)</title>', r.text, re.DOTALL)[0]
                    links.append((url,title))
                    
                    # Save to DB
                    for url, title in links:
                        print(sender, subject, date, body, url, title)
                        cur.execute('INSERT INTO Emails (sender,subject,date,body,links) VALUES (%s,%s,%s,%s,%s)', (sender,subject,date,body,f'{title} - {url}'))
                        dbConnect.commit()
print("Finished extracting. Data saved to spreadsheet.")

        
        

    