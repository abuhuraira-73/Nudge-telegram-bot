import os
import json
import logging
import urllib.parse
import requests
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from config import Config

# Scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_FILE = 'credentials.json'

def get_client_config():
    """Gets the client config from env or file."""
    env_creds = os.getenv("GOOGLE_CREDENTIALS_JSON")
    data = None
    if env_creds:
        try:
            data = json.loads(env_creds)
        except Exception as e:
            logging.error(f"Error parsing GOOGLE_CREDENTIALS_JSON: {e}")
    
    elif os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logging.error(f"Error reading credentials.json: {e}")

    if data:
        # Support both 'web' (Cloud) and 'installed' (Desktop) types
        return data.get('web') or data.get('installed')
    
    return None

def get_redirect_uri():
    """Returns the redirect URI for OAuth."""
    if Config.WEB_URL:
        return f"{Config.WEB_URL.rstrip('/')}/callback"
    return "http://localhost"

def get_auth_url(user_id: int):
    """
    Generates the Google authorization URL manually.
    """
    client_config = get_client_config()
    if not client_config:
        logging.error("Google Client Config not found!")
        return None
    
    params = {
        'client_id': client_config['client_id'],
        'redirect_uri': get_redirect_uri(),
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
        'state': str(user_id) # Pass user_id to the callback
    }
    return f"{client_config['auth_uri']}?{urllib.parse.urlencode(params)}"

def exchange_code(auth_code):
    """
    Exchanges an authorization code for a token.
    """
    client_config = get_client_config()
    if not client_config:
        raise Exception("Google Credentials not configured.")
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': auth_code,
        'client_id': client_config['client_id'],
        'client_secret': client_config['client_secret'],
        'redirect_uri': get_redirect_uri(),
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
            
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        logging.error(f"Error building calendar service: {e}")
        return None
