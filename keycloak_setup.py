import requests

KEYCLOAK_URL = "http://localhost:8080"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"
REALM = "saas-platform"
CLIENT_ID = "saas-frontend"
USER_NAME = "testuser"
USER_PASS = "testpass"

# 1. Get admin access token
def get_admin_token():
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": ADMIN_USER,
        "password": ADMIN_PASS
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

# 2. Create realm
def create_realm(token):
    url = f"{KEYCLOAK_URL}/admin/realms"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "realm": REALM,
        "enabled": True
    }
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 409:
        print(f"Realm '{REALM}' already exists.")
    else:
        resp.raise_for_status()
        print(f"Realm '{REALM}' created.")

# 3. Create client
def create_client(token):
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/clients"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "clientId": CLIENT_ID,
        "enabled": True,
        "publicClient": True,
        "redirectUris": ["http://localhost:3000/*"],
        "webOrigins": ["http://localhost:3000"],
        "protocol": "openid-connect"
    }
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 409:
        print(f"Client '{CLIENT_ID}' already exists.")
    else:
        resp.raise_for_status()
        print(f"Client '{CLIENT_ID}' created.")

# 4. Create user
def create_user(token):
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "username": USER_NAME,
        "enabled": True
    }
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 409:
        print(f"User '{USER_NAME}' already exists.")
    else:
        resp.raise_for_status()
        print(f"User '{USER_NAME}' created.")
    # Get user ID
    resp = requests.get(url, headers=headers, params={"username": USER_NAME})
    user_id = resp.json()[0]["id"]
    # Set password
    url_pw = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/reset-password"
    pw_data = {
        "type": "password",
        "value": USER_PASS,
        "temporary": False
    }
    resp = requests.put(url_pw, json=pw_data, headers=headers)
    resp.raise_for_status()
    print(f"Password set for user '{USER_NAME}'.")

if __name__ == "__main__":
    token = get_admin_token()
    create_realm(token)
    create_client(token)
    create_user(token)
    print("Keycloak setup complete.")
