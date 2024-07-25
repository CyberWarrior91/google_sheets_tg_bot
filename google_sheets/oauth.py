from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def authorize_google_sheets():
    """Initiates the Google Sheets API authorization flow."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        return creds 
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        # Handle refresh token expiration or revocation
        print("Refresh token expired or revoked. Re-authenticating...")
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(open_browser=False, port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds
    # Return the credentials if already authorized