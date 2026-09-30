import requests
import json
import urllib3

BASE_URL = "https://re-cluster1.ps-redislabs.org:9443/v1"
AUTH = ("admin@rl.org", "bP0Pmxs")
HEADERS = {"Content-Type": "application/json"}

def create_database():
    """Create a new database without using any modules."""
    endpoint = f"{BASE_URL}/bdbs"
    payload = {
        "name": "api-demo-db",
        "memory_size": 1073741824,
        "type": "redis",
        "module_list": []          
    }
    
    print("1. Creating new database...")
    response = requests.post(endpoint, auth=AUTH, headers=HEADERS, json=payload, verify=False)
    
    if response.status_code in [200, 202]:
        db_data = response.json()
        db_id = db_data.get("uid")
        print(f"   Database created successfully! (ID: {db_id})")
        return db_id
    else:
        print(f"   Failed to create database: {response.status_code} - {response.text}")
        return None

def create_users():
    """Create three new users with specified roles."""
    endpoint = f"{BASE_URL}/users"
    users_to_create = [
        {"email": "john.doe@example.com", "name": "John Doe", "role": "db_viewer"},
        {"email": "mike.smith@example.com", "name": "Mike Smith", "role": "db_member"},
        {"email": "cary.johnson@example.com", "name": "Cary Johnson", "role": "admin"}
    ]
    
    print("\n2. Creating users...")
    for user in users_to_create:
        payload = {
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "password": "bP0Pmxs" 
        }
        res = requests.post(endpoint, auth=AUTH, headers=HEADERS, json=payload, verify=False)
        if res.status_code in [200, 201]:
            print(f"   Created user: {user['name']} ({user['role']})")
            
        else:
            print(f"   Failed to create user {user['name']}: {res.status_code} - {res.text}")

def list_and_display_users():
    """Fetch and display all users in (name, role, email) format."""
    endpoint = f"{BASE_URL}/users"
    print("\n3. Listing all users:")
    res = requests.get(endpoint, auth=AUTH, verify=False)
    
    if res.status_code == 200:
        users = res.json()
        for user in users:
            name = user.get("name", "N/A")
            role = user.get("role", "N/A")
            email = user.get("email", "N/A")
            print(f"   Name: {name} | Role: {role} | Email: {email}")
    else:
        print(f"   Failed to retrieve users: {res.status_code} - {res.text}")

def delete_database(db_id):
    """Delete the previously created database."""
    if not db_id:
        print("\n4. Skipping database deletion: No valid database ID found.")
        return

    endpoint = f"{BASE_URL}/bdbs/{db_id}"
    print(f"\n4. Deleting database (ID: {db_id})...")
    res = requests.delete(endpoint, auth=AUTH, verify=False)
    
    if res.status_code in [200, 202, 204]:
        print("   Database deleted successfully!")
    else:
        print(f"   Failed to delete database: {res.status_code} - {res.text}")

def main():
    db_id = create_database()
    create_users()
    list_and_display_users()
    delete_database(db_id)

if __name__ == "__main__":
    main()