
import requests
import json
from django.conf import settings
from django.core.cache import cache

class SMSService:
    """
    Service to handle SMS sending via external API.
    Implements Client Credentials flow for auth.
    """
    
    def __init__(self):
        self.client_id = settings.SMS_CLIENT_ID
        self.client_secret = settings.SMS_CLIENT_SECRET
        self.auth_url = settings.SMS_AUTH_URL
        self.single_url = settings.SMS_SINGLE_URL
        self.bulk_url = settings.SMS_BULK_URL
        self.sender_id = settings.SMS_SENDER_ID

    def get_access_token(self):
        """
        Retrieves access token, using cache to avoid frequent auth calls.
        """
        token = cache.get('sms_access_token')
        if token:
            return token
            
        try:
            # Assuming standard JSON payload for auth
            payload = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            response = requests.post(self.auth_url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)
            
            if token:
                # Cache user for slightly less time than expiry to be safe
                cache.set('sms_access_token', token, timeout=expires_in - 60)
                return token
        except Exception as e:
            print(f"Error fetching SMS token: {e}")
            return None
            
        return None

    def send_single_sms(self, phone_number, message):
        """
        Sends a single SMS.
        """
        token = self.get_access_token()
        if not token:
            return False, "Authentication failed"
            
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'sender': self.sender_id,
            'mobile': phone_number,
            'message': message
        }
        
        try:
            response = requests.post(self.single_url, json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                return True, "Sent"
            return False, f"API Error: {response.text}"
        except Exception as e:
            return False, str(e)

    def send_bulk_sms(self, phone_numbers, message):
        """
        Sends bulk SMS.
        phone_numbers: List of strings
        """
        token = self.get_access_token()
        if not token:
            return False, "Authentication failed"
            
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Adjust payload based on specific provider format. 
        # Common format: list of numbers
        payload = {
            'sender': self.sender_id,
            'mobiles': phone_numbers, # or 'numbers': ...
            'message': message
        }
        
        try:
            response = requests.post(self.bulk_url, json=payload, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                return True, "Queued/Sent"
            return False, f"API Error: {response.text}"
        except Exception as e:
            return False, str(e)
            
    def send_message(self, recipients, message):
        """
        Router for sending messaging.
        recipients: list of phone numbers.
        """
        # Clean numbers (remove None/Empty)
        valid_recipients = [r for r in recipients if r]
        
        if not valid_recipients:
            return False, "No valid recipients"
            
        if len(valid_recipients) == 1:
            return self.send_single_sms(valid_recipients[0], message)
        else:
            return self.send_bulk_sms(valid_recipients, message)
