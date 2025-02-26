import requests
import time
import re
import json
from access_token import get_flip_access_token
from dotenv import load_dotenv
import logging
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

BASE_URL = os.getenv('BASE_URL')

def format_phone_number(phone):
    if not phone:
        return "+18888888888"  # Default phone number
    
    # Strip all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # If no digits, return default
    if not digits_only:
        return "+18888888888"
    
    # Check if it's missing both + and country code
    if len(digits_only) == 10:
        return f"+1{digits_only}"
    
    # Check if it's just missing the + sign but has country code
    if not phone.startswith('+'):
        return f"+{digits_only}"
    
    # Already properly formatted
    return phone

def extract_error_message(response_text):
    try:
        # Parse the response JSON
        error_data = json.loads(response_text)
        
        # Check for different error message patterns
        if 'message' in error_data:
            return error_data['message']
        elif 'error' in error_data and isinstance(error_data['error'], str):
            return error_data['error']
        elif 'errors' in error_data and isinstance(error_data['errors'], list) and len(error_data['errors']) > 0:
            # Combine multiple error messages if present
            messages = [err.get('message', '') for err in error_data['errors'] if 'message' in err]
            if messages:
                return '; '.join(messages)
        
        # Fallback to the entire response if no specific message found
        return f"API Error: {response_text}"
    except Exception as e:
        logging.error(f"Error parsing API error response: {e}")
        return f"API Error: {response_text[:100]}..."  # Truncate long responses

def create_brands(brand_name, company_name, main_contact_name, vendor_email, 
                  description=None, founded_year=None, country=None, 
                  instagram=None, website=None, phone=None):
    url = f'{BASE_URL}/shop/admin/brands/onboarding/outbound/v1'
    
    # Validate all mandatory fields
    missing_fields = []
    
    if not brand_name:
        missing_fields.append("brand name")
    
    if not company_name:
        missing_fields.append("company name")
    
    if not main_contact_name:
        missing_fields.append("main contact name")
    
    if not vendor_email:
        missing_fields.append("vendor email")
    
    if missing_fields:
        field_list = ", ".join(missing_fields)
        return {"error": f"Missing mandatory fields: {field_list}"}
    
    # Format the phone number to include plus sign
    formatted_phone = format_phone_number(phone)
    if formatted_phone != phone:
        logging.info(f"Formatted phone number from '{phone}' to '{formatted_phone}'")
    
    access_token = get_flip_access_token()  # Retrieves a fresh token
    logging.info("Using access token: %s", access_token)
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {access_token}',
        'content-type': 'application/json',
        'origin': 'https://flipmagic.flip.shop',
        'priority': 'u=1, i',
        'referer': 'https://flipmagic.flip.shop/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }
    
    # Set default values for optional fields
    payload = {
        "name": brand_name,
        "companyName": company_name,
        "description": description or "description",
        "categoryList": ["other"],
        "foundedInYear": founded_year or 2024,
        "countryOfOrigin": country or "United States",
        "instagramUrl": instagram or "instagram.com",
        "websiteUrl": website or "website.com",
        "vendorMainContactEmail": vendor_email,
        "mainContactName": main_contact_name,
        "sales": "from1To5mln",
        "mainContactPhone": formatted_phone,
        "genders": ["unisex"],
        "brandGoalsOnFlip": ["increaseSales"]
    }
    
    # Convert foundedInYear to integer if it's a string
    try:
        if isinstance(payload["foundedInYear"], str) and payload["foundedInYear"].strip():
            payload["foundedInYear"] = int(payload["foundedInYear"])
    except ValueError:
        logging.warning(f"Invalid foundedInYear value: {payload['foundedInYear']}. Using default 2024.")
        payload["foundedInYear"] = 2024
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        logging.info("Successfully processed brand: %s", brand_name)
        logging.info("API response: %s", result)
        return result
    except requests.exceptions.RequestException as e:
        logging.error("Error processing brand %s: %s", brand_name, e)
        
        # Extract and return a user-friendly error message
        if hasattr(e, 'response') and e.response is not None:
            error_text = e.response.text
            logging.error("Response content: %s", error_text)
            
            # Extract user-friendly error message
            user_error = extract_error_message(error_text)
            return {"error": user_error}
        
        return {"error": str(e)}