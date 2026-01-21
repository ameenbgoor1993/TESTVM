import urllib.request
import urllib.parse
import json
import urllib.error

url = "http://127.0.0.1:8000/api/login/"
# Use the user created in verify_registration (or any valid user)
username = "volunteer_0"
password = "password123"

data = json.dumps({'username': username, 'password': password}).encode('utf-8')
headers = {'Content-Type': 'application/json'}
req = urllib.request.Request(url, data=data, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.getcode()}")
        print(f"Body: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
