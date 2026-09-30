import requests
import json
import urllib3

# Disable SSL verification warnings for self-signed lab certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API Configuration
# Replace hostname with node IP (e.g., https://172.16.22.21:9443) if DNS fails
BASE_URL = "https://re-cluster1.ps-redislabs.org:9443/v1"
AUTH = ("admin@rl.org", "bP0Pmxs")
HEADERS = {"Content-Type": "application/json"}

# Global variable to store created DB ID during menu execution
created_db_id = None

def create_database():
    """1. Create a new database without using any modules."""
    global created_db_id
    endpoint = f"{BASE_URL}/bdbs"
    payload = {
        "name": "api-demo-db",
        "memory_size": 1073741824,  # 1GB in bytes
        "type": "redis",
        "module_list": []           # No modules
    }
    
    print("\n[+] Creating new database...")
    try:
        response = requests.post(endpoint, auth=AUTH, headers=HEADERS, json=payload, verify=False)
        if response.status_code in [200, 202]:
            db_data = response.json()
            created_db_id = db_data.get("uid")
            print(f"    Success! Database created with ID: {created_db_id}")
        else:
            print(f"    Failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"    Error: {e}")

def create_users():
    """2. Create three new users with specified roles."""
    endpoint = f"{BASE_URL}/users"
    users_to_create = [
        {"email": "john.doe@example.com", "name": "John Doe", "role": "admin"},
        {"email": "mike.smith@example.com", "name": "Mike Smith", "role": "admin"},
        {"email": "cary.johnson@example.com", "name": "Cary Johnson", "role": "admin"}
    ]
    
    print("\n[+] Creating users...")
    for user in users_to_create:
        payload = {
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "password": "Password123!"  # Password required by API
        }
        try:
            res = requests.post(endpoint, auth=AUTH, headers=HEADERS, json=payload, verify=False)
            if res.status_code in [200, 201]:
                print(f"    Created: {user['name']} | Role: {user['role']} | Email: {user['email']}")
            else:
                print(f"    Failed to create {user['name']} ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"    Error creating {user['name']}: {e}")

def list_and_display_users():
    """3. Fetch and display all users in (name, role, email) format."""
    endpoint = f"{BASE_URL}/users"
    print("\n[+] Fetching user list...")
    try:
        res = requests.get(endpoint, auth=AUTH, verify=False)
        if res.status_code == 200:
            users = res.json()
            print("\n--- Current Cluster Users ---")
            for u in users:
                name = u.get("name", "N/A")
                role = u.get("role", "N/A")
                email = u.get("email", "N/A")
                print(f"Name: {name:<20} | Role: {role:<12} | Email: {email}")
            print("------------------------------")
        else:
            print(f"    Failed ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"    Error: {e}")

def delete_database():
    """4. Delete the database (prompts for ID if not already saved in memory)."""
    global created_db_id
    db_id = created_db_id
    
    if not db_id:
        db_id = input("Enter the Database ID (UID) to delete: ").strip()
        
    if not db_id:
        print("    No Database ID provided. Aborting deletion.")
        return

    endpoint = f"{BASE_URL}/bdbs/{db_id}"
    print(f"\n[+] Deleting database ID: {db_id}...")
    try:
        res = requests.delete(endpoint, auth=AUTH, verify=False)
        if res.status_code in [200, 202, 204]:
            print("    Database deleted successfully!")
            created_db_id = None
        else:
            print(f"    Failed ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"    Error: {e}")

def main():
    while True:
        print("\n======================================")
        print("   Redis Enterprise REST API Menu")
        print("======================================")
        print("1. Create New Database")
        print("2. Create Three Users")
        print("3. List and Display Users")
        print("4. Delete Database")
        print("5. Execute ALL Steps (Sequential)")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ").strip()

        if choice == "1":
            create_database()
        elif choice == "2":
            create_users()
        elif choice == "3":
            list_and_display_users()
        elif choice == "4":
            delete_database()
        elif choice == "5":
            create_database()
            create_users()
            list_and_display_users()
            delete_database()
        elif choice == "6":
            print("Exiting script.")
            break
        else:
            print("Invalid selection. Please choose a number between 1 and 6.")

if __name__ == "__main__":
    main()