# import os
# import json
# import time
# import requests
# import logging
# from dotenv import load_dotenv

# load_dotenv()

# # Logging setup
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# BASE_URL = os.getenv('BASE_URL')
# REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
# APP_PLATFORM = os.getenv('APP_PLATFORM')
# WEB_VERSION = os.getenv('WEB_VERSION')
# DEVICE_FP = os.getenv('DEVICE_FP')
# GET_ACCESS_TOKEN_THROUGH_REFRESH_TOKEN_PATH = os.getenv('GET_ACCESS_TOKEN_THROUGH_REFRESH_TOKEN_PATH')
# ACCESS_TOKEN_FILE_PATH = os.getenv('ACCESS_TOKEN_FILE_PATH')
# TOKEN_FILE = os.getenv("ACCESS_TOKEN_FILE_PATH", "token.json")

# def store_token_data(data):
#     with open(TOKEN_FILE, 'w') as file:
#         json.dump(data, file)

# def load_token_data():
#     if os.path.exists(TOKEN_FILE):
#         with open(TOKEN_FILE, 'r') as file:
#             return json.load(file)
#     return None

# def is_token_valid(token_data):
#     # current time in milliseconds
#     current_time = int(time.time() * 1000)
#     return token_data and current_time < token_data['data']['auth']['expiresAt']

# def refresh_access_token():
#     url = BASE_URL + GET_ACCESS_TOKEN_THROUGH_REFRESH_TOKEN_PATH
#     headers = {
#         "App-Platform": APP_PLATFORM,
#         "web-version": WEB_VERSION,
#         "device-fp": DEVICE_FP,
#     }
#     parameters = {
#         "refreshToken": REFRESH_TOKEN
#     }
#     response = requests.post(url=url, headers=headers, json=parameters)
#     if response.status_code == 200:
#         token_data = response.json()
#         store_token_data(token_data)
#         return token_data['data']['auth']['accessToken']

#     logger.error(f"Failed to refresh access token. Status code: {response.status_code}")
#     return None

# def get_flip_access_token():
#     token_data = load_token_data()
#     if token_data and is_token_valid(token_data):
#         return token_data['data']['auth']['accessToken']
#     logger.info("Access token is missing or expired. Refreshing token...")
#     return refresh_access_token()

# if __name__ == "__main__":
#     token = get_flip_access_token()
#     if token:
#         print("Access token retrieved:", token)
#     else:
#         print("Failed to retrieve access token")
import os
import json
import time
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Config from environment variables
BASE_URL = os.getenv('BASE_URL')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
APP_PLATFORM = os.getenv('APP_PLATFORM')
WEB_VERSION = os.getenv('WEB_VERSION')
DEVICE_FP = os.getenv('DEVICE_FP')
GET_ACCESS_TOKEN_THROUGH_REFRESH_TOKEN_PATH = os.getenv('GET_ACCESS_TOKEN_THROUGH_REFRESH_TOKEN_PATH')

# In-memory token cache
TOKEN_CACHE = {
    'data': None,
    'last_updated': None
}

def store_token_data(data):
    TOKEN_CACHE['data'] = data
    TOKEN_CACHE['last_updated'] = datetime.now().timestamp()
    logger.info("Token stored in memory cache")

def load_token_data():
    return TOKEN_CACHE['data']

def is_token_valid(token_data):
    if not token_data:
        return False
        
    # Current time in milliseconds
    current_time = int(time.time() * 1000)
    
    # Check token expiration
    if current_time >= token_data['data']['auth']['expiresAt']:
        logger.info("Token has expired")
        return False
        
    return True

def refresh_access_token():
    if not REFRESH_TOKEN:
        logger.error("REFRESH_TOKEN environment variable is not set")
        return None
        
    url = BASE_URL + GET_ACCESS_TOKEN_THROUGH_REFRESH_TOKEN_PATH
    headers = {
        "App-Platform": APP_PLATFORM,
        "web-version": WEB_VERSION,
        "device-fp": DEVICE_FP,
    }
    parameters = {
        "refreshToken": REFRESH_TOKEN
    }
    
    try:
        response = requests.post(url=url, headers=headers, json=parameters)
        response.raise_for_status()
        token_data = response.json()
        store_token_data(token_data)
        logger.info("Successfully refreshed access token")
        return token_data['data']['auth']['accessToken']
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to refresh access token: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        return None

def get_flip_access_token():
    token_data = load_token_data()
    
    if is_token_valid(token_data):
        logger.info("Using cached access token")
        return token_data['data']['auth']['accessToken']
        
    logger.info("Access token is missing or expired. Refreshing token...")
    return refresh_access_token()

if __name__ == "__main__":
    token = get_flip_access_token()
    if token:
        print("Access token retrieved:", token)
    else:
        print("Failed to retrieve access token")