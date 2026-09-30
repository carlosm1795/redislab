import requests
import json
import urllib3

# Disable SSL warnings for self-signed lab certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API Configuration
# If hostname resolution fails inside the lab, replace with node IP (e.g., "https://172.16.22.21:9443/v1")
BASE_URL = "https://re-cluster1.ps-redislabs.org:9443/v1"
AUTH = ("admin@rl.org", "bP0Pmxs")
HEADERS = {"Content-Type": "application/json"}

created_db_id = None

def get_exact_role_name(target_role):
    """
    Queries /v1/roles to get the exact role name required by Redis Enterprise.
    """
    try:
        res = requests.get(f"{BASE_URL}/roles", auth=AUTH, verify=False)
        if res.status_code == 200:
            roles = res.json()
            for r in roles:
                r_name = r.get("name", "")
                # Flexible matching for db_viewer, db_member, admin
                if target_role.lower() in r_name.lower().replace(" ", "_") or target_role.lower() in r_name.lower():
                    return r_name
    except Exception as e:
        print(f"    Warning fetching roles: {e}")
    
    # Defaults fallback if API query fails
    fallback_map = {
        "db_viewer": "DB Viewer",
        "db_member": "DB Member",
        "admin": "Cluster Admin"
    }
    return fallback_map.get(target_role, target_role)

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
        # Note: Redis Enterprise API accepts role as an array of role names
        payload = {
            "email": user["email"],
            "name": user["name"],
            "role": [user["role"]],     # Role passed as an array [ "DB Viewer" ]
            "password": "Password123!"
        }
        try:
            res = requests.post(endpoint, auth=AUTH, headers=HEADERS, json=payload, verify=False)
            if res.status_code in [200, 201]:
                print(f"    Successfully created: {user['name']} | Role: {user['role']} | Email: {user['email']}")
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
                
                # Format role output cleanly whether returned as string or list
                raw_role = u.get("role") or u.get("roles")
                if isinstance(raw_role, list):
                    role_str = ", ".join(raw_role)
                else:
                    role_str = str(raw_role)
                    
                email = u.get("email", "N/A")
                print(f"Name: {name:<20} | Role: {role_str:<15} | Email: {email}")
            print("------------------------------")
        else:
            print(f"    Failed ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"    Error: {e}")

def delete_database():
    """4. Delete the database."""
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