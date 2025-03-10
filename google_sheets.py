import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


scopes = ["https://www.googleapis.com/auth/spreadsheets"]

sheet_id = '1zDN_7DCoA3jdfNll_ZONZtD2XMgtHGIFyzHEQBwiF6M'

def get_credentials():
    """Get and return valid credentials for Google Sheets API"""
    credentials = None
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', scopes)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
            credentials = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
    
    return credentials

def get_sheets_service():
    """Get authenticated Google Sheets service"""
    credentials = get_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    return service.spreadsheets()

def main():
    """Test authentication and connection"""
    credentials = get_credentials()
    if credentials and credentials.valid:
        print("Google Sheets authentication successful.")
        return True
    else:
        print("Failed to authenticate with Google Sheets.")
        return False

if __name__ == '__main__':
    main()