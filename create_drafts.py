import os
import re
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_draft(service, to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft = service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()
    print(f"✅ Draft created for {to}: {subject}")
    return draft

# Load saved gmail output
with open("gmail_output.txt", "r") as f:
    gmail_output = f.read()

gmail_service = get_gmail_service()

# Split by EMAIL blocks
email_blocks = re.split(r'---\s*\n## EMAIL \d+', gmail_output)

drafts_created = 0
skipped = 0
for block in email_blocks:
    try:
        subject_match = re.search(r'\*\*Subject Line:\*\*\s*(.+)', block)
        body_match = re.search(r'\*\*Body:\*\*\s*\n(.*?)(?=---|\Z)', block, re.DOTALL)
        email_match = re.search(r'\*\*Recipient Email:\*\*\s*([^\s*]+@[^\s*]+)', block)

        if subject_match and body_match and email_match:
            subject = subject_match.group(1).strip()
            body = body_match.group(1).strip()
            to = email_match.group(1).strip()

            # Skip invalid or placeholder emails
            if '@' not in to or 'to be verified' in to.lower() or '[' in to:
                print(f"⚠️ Skipping invalid email: {to}")
                skipped += 1
                continue

            create_draft(gmail_service, to, subject, body)
            drafts_created += 1
    except Exception as e:
        print(f"❌ Could not create draft: {e}")

print(f"\n🎉 {drafts_created} Gmail drafts created successfully")
print(f"⚠️ {skipped} emails skipped due to invalid or unverified addresses")