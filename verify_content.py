import urllib.request
import json
import urllib.error

# Verify Blog List API
url = "http://127.0.0.1:8000/api/content/blogs/"

try:
    with urllib.request.urlopen(url) as response:
        print(f"Status: {response.getcode()}")
        body = response.read().decode('utf-8')
        data = json.loads(body)
        print(f"Status in JSON: {data.get('status')}")
        print(f"Message: {data.get('message')}")
        print("Structure seems correct.")
except Exception as e:
    print(f"Error: {e}")
