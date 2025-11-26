"""
Authentication module - OAuth 2.0 and Service Account support
"""

import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'client_secret.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'service_account.json')

# Authentication method: auto, oauth, service_account
AUTH_METHOD = os.getenv('AUTH_METHOD', 'auto').lower()


def get_credentials():
    """Get credentials based on AUTH_METHOD setting"""
    if AUTH_METHOD == 'service_account':
        print("  [AUTH] Using service account")
        return _get_service_account_credentials()
    elif AUTH_METHOD == 'oauth':
        print("  [AUTH] Using OAuth 2.0")
        return _get_oauth_credentials()
    else:  # auto
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            print("  [AUTH] Auto-detected service account")
            return _get_service_account_credentials()
        print("  [AUTH] Auto-detected OAuth 2.0")
        return _get_oauth_credentials()


def _get_service_account_credentials():
    """Get service account credentials"""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )


def _get_oauth_credentials():
    """Get OAuth credentials, refreshing or re-authenticating as needed"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(f"OAuth client secret not found: {CLIENT_SECRET_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds
