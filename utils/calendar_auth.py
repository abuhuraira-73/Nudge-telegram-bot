import os
import json
import logging
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_FILE = 'credentials.json'

def get_flow():
    """
    Creates a Flow object for the OAuth 2.0 process.
    """
    return Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob' # Standard for manual code exchange
    )

def get_auth_url():
    """
    Generates the Google authorization URL manually.
    Uses http://localhost as the redirect_uri.
    """
    with open(CREDENTIALS_FILE, 'r') as f:
        config = json.load(f)
    client_config = config['installed']
    
    import urllib.parse
    params = {
        'client_id': client_config['client_id'],
        'redirect_uri': 'http://localhost',
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f"{client_config['auth_uri']}?{urllib.parse.urlencode(params)}"

def exchange_code(auth_code):
    """
    Exchanges an authorization code for a token.
    Uses http://localhost as the redirect_uri.
    """
    import requests
    
    with open(CREDENTIALS_FILE, 'r') as f:
        config = json.load(f)
    client_config = config['installed']
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': auth_code,
        'client_id': client_config['client_id'],
        'client_secret': client_config['client_secret'],
        'redirect_uri': 'http://localhost',
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    response_data = response.json()
    
    if 'error' in response_data:
        logging.error(f"Google Token Exchange Error: {response_data}")
        raise Exception(f"Google Token Exchange Error: {response_data.get('error_description')}")
        
    token_info = {
        'token': response_data.get('access_token'),
        'refresh_token': response_data.get('refresh_token'),
        'token_uri': token_url,
        'client_id': client_config['client_id'],
        'client_secret': client_config['client_secret'],
        'scopes': SCOPES
    }
    
    return json.dumps(token_info)

def get_calendar_service(token_json):
    """
    Returns an authorized Google Calendar service object.
    Handles token refresh if needed.
    """
    try:
        creds_data = json.loads(token_json)
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        
        if creds and creds.expired and creds.refresh_token:
            logging.info("Refreshing Google Calendar access token...")
            creds.refresh(Request())
            # Note: We should ideally save the refreshed token back to the DB here,
            # but for simplicity, we'll return the service and let the caller handle it if needed.
            # In our case, the service object will work.
            
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        logging.error(f"Error building calendar service: {e}")
        return None
