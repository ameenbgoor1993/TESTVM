import json

with open('VMS.postman_collection.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# FindAUTH folder
auth_folder = next(item for item in data['item'] if item['name'] == 'AUTH')

# Add Child Request
add_child_req = {
    "name": "Add Child Profile",
    "request": {
    "auth": {
        "type": "bearer",
        "bearer": [
        {
            "key": "token",
            "value": "{{token}}",
            "type": "string"
        }
        ]
    },
    "method": "POST",
    "header": [],
    "body": {
        "mode": "raw",
        "raw": "{\n    \"first_name\": \"Child1\",\n    \"last_name\": \"Doe\",\n    \"date_of_birth\": \"2010-01-01\",\n    \"gender\": 1,\n    \"user_type\": 2\n}",
        "options": {
        "raw": {
            "language": "json"
        }
        }
    },
    "url": {
        "raw": "http://localhost:8080/api/profiles/add-child/",
        "protocol": "http",
        "host": [
        "localhost"
        ],
        "port": "8080",
        "path": [
        "api",
        "profiles",
        "add-child",
        ""
        ]
    }
    },
    "response": []
}

# Insert after Register Step 3
step3_idx = next(i for i, req in enumerate(auth_folder['item']) if req['name'] == 'Register Step 3')
auth_folder['item'].insert(step3_idx + 1, add_child_req)

with open('VMS.postman_collection.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Postman collection updated successfully.")
