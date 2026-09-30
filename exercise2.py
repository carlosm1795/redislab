import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://re-cluster1.ps-redislabs.org:9443/v1"
AUTH = ("admin@rl.org", "bP0Pmxs")
HEADERS = {"Content-Type": "application/json"}

created_db_id = None

def get_role_map():
    """Fetches all existing roles and maps name -> uid."""
    role_map = {}
    try:
        res = requests.get(f"{BASE_URL}/roles", auth=AUTH, verify=False)
        if res.status_code == 200:
            for r in res.json():
                role_map[r.get("name").lower()] = r.get("uid")
    except Exception as e:
        print(f"    Error querying roles: {e}")
    return role_map

def create_roles():
    """1. Create the custom db_viewer and db_member roles."""
    endpoint = f"{BASE_URL}/roles"
    
    roles_to_create = [
        {
            "name": "db_viewer",
            "permissions": [
                {"name": "view_all_bdbs_info"},
                {"name": "view_all_users_info"}
            ]
        },
        {
            "name": "db_member",
            "permissions": [
                {"name": "view_all_bdbs_info"},
                {"name": "view_bdb_stats"},
                {"name": "view_all_users_info"}
            ]
        }
    ]
    
    print("\n[+] Creating Roles...")
    for role in roles_to_create:
        try:
            res = requests.post(endpoint, auth=AUTH, headers=HEADERS, json=role, verify=False)
            if res.status_code in [200, 201]:
                data = res.json()
                print(f"    Role '{role['name']}' created successfully (UID: {data.get('uid')})")
            elif res.status_code in [400, 409]:
                print(f"    Role '{role['name']}' already exists.")
            else:
                print(f"    Failed ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"    Error: {e}")

def create_database():
    """2. Create a new database without modules."""
    global created_db_id
    endpoint = f"{BASE_URL}/bdbs"
    payload = {
        "name": "api-demo-db",
        "memory_size": 1073741824,  # 1GB
        "type": "redis",
        "module_list": []
    }
    
    print("\n[+] Creating new database...")
    try:
        response = requests.post(endpoint, auth=AUTH, headers=HEADERS, json=payload, verify=False)
        if response.status_code in [200, 202]:
            created_db_id = response.json().get("uid")
            print(f"    Success! Database created with ID: {created_db_id}")
        else:
            print(f"    Failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"    Error: {e}")

def create_users():
    """3. Create three users using role_uids."""
    endpoint = f"{BASE_URL}/users"
    role_map = get_role_map()
    
    admin_uid = role_map.get("admin")
    viewer_uid = role_map.get("db_viewer") or admin_uid
    member_uid = role_map.get("db_member") or admin_uid

    users_to_create = [
        {"email": "john.doe@example.com", "name": "John Doe", "role_uids": [viewer_uid]},
        {"email": "mike.smith@example.com", "name": "Mike Smith", "role_uids": [member_uid]},
        {"email": "cary.johnson@example.com", "name": "Cary Johnson", "role_uids": [admin_uid]}
    ]
    
    print("\n[+] Creating users...")
    for user in users_to_create:
        payload = {
            "email": user["email"],
            "name": user["name"],
            "role_uids": user["role_uids"],
            "password": "Password123!"
        }
        try:
            res = requests.post(endpoint, auth=AUTH, headers=HEADERS, json=payload, verify=False)
            if res.status_code in [200, 201]:
                print(f"    Created: {user['name']} | Role UIDs: {user['role_uids']} | Email: {user['email']}")
            else:
                print(f"    Failed to create {user['name']} ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"    Error: {e}")

def list_and_display_users():
    """4. Fetch and display users in (name, role, email) format."""
    endpoint = f"{BASE_URL}/users"
    print("\n[+] Fetching user list...")
    try:
        res = requests.get(endpoint, auth=AUTH, verify=False)
        if res.status_code == 200:
            print("\n--- Current Cluster Users ---")
            for u in res.json():
                name = u.get("name", "N/A")
                role_info = u.get("role_uids") or u.get("role") or "N/A"
                email = u.get("email", "N/A")
                print(f"Name: {name:<20} | Role/Role UIDs: {str(role_info):<15} | Email: {email}")
            print("------------------------------")
        else:
            print(f"    Failed ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"    Error: {e}")

def delete_database():
    """5. Delete the database."""
    global created_db_id
    db_id = created_db_id or input("Enter Database ID to delete: ").strip()
    if not db_id:
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
        print("1. Create 'db_viewer' & 'db_member' Roles")
        print("2. Create New Database")
        print("3. Create Three Users")
        print("4. List and Display Users")
        print("5. Delete Database")
        print("6. Execute ALL Steps (Sequential)")
        print("7. Exit")
        
        choice = input("\nSelect an option (1-7): ").strip()

        if choice == "1":
            create_roles()
        elif choice == "2":
            create_database()
        elif choice == "3":
            create_users()
        elif choice == "4":
            list_and_display_users()
        elif choice == "5":
            delete_database()
        elif choice == "6":
            create_roles()
            create_database()
            create_users()
            list_and_display_users()
            delete_database()
        elif choice == "7":
            break

if __name__ == "__main__":
    main()