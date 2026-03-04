import json
import urllib.request
import urllib.error

url = "http://127.0.0.1:8000/api/register/"

import random
suffix = str(random.randint(1000, 9999))
payload = {
    "username": f"testvolunteer_api_v{suffix}",
    "password": "securepassword123",
    "email": f"testvolunteer_api_v{suffix}@example.com",
    "first_name_en": "Jane",
    "middle_name_en": "Marie",
    "last_name_en": "Doe",
    "first_name_ar": "جين",
    "middle_name_ar": "ماري",
    "last_name_ar": "دو",
    "gender": 2,
    "birthdate": "1998-08-20",
    "nationality": "Canadian",
    "national_id": f"98765432{suffix}",
    "profession": "Doctor",
    "mobile_no": "+0987654321",
    "address": "456 Health Ave, Toronto",
    "emergency_contact": "+1122334455"
}

headers = {
    'Content-Type': 'application/json'
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        response_body = response.read().decode('utf-8')
        print(f"Status Code: {status_code}")
        print(f"Response Body: {response_body}")
        
        if status_code == 201 or status_code == 200:
            try:
                resp_json = json.loads(response_body)
                if resp_json.get('status') is True and 'data' in resp_json:
                     print("SUCCESS: Response structure verified.")
                else:
                     print("FAILURE: Incorrect response structure.")
            except:
                print("FAILURE: Could not parse JSON.")
        else:
            print(f"FAILURE: Unexpected status code {status_code}.")

except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"An error occurred: {e}")
