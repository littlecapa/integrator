import json
import os
import platform

import msal
import requests


def get_config():
    if platform.system() == "Darwin":  # macOS
        download_dir = os.path.expanduser("~/Downloads")
    elif platform.system() == "Windows": #Windows
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    else: #Linux
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    config_file = os.path.join(download_dir, "OneDriveConfig.json")
    print(f"Config file: {config_file}")

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_file}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {config_file}")
        return None

# Microsoft Graph API endpoint
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"

# Function to acquire an access token
#
# https://msal-python.readthedocs.io/en/latest/#msal.ConfidentialClientApplication
#

def get_access_token(config):
    authority = f"https://login.microsoftonline.com/{config['DIRECTORY_ID']}"
    app = msal.ConfidentialClientApplication(
        config['CLIENT_ID'], authority=authority, client_credential=config['CLIENT_SECRET']
    )
    scopes = [f"{scope}/.default" for scope in config["SCOPES"]]
    scopes = ["https://graph.microsoft.com/.default"]
    print(f"Scopes: {scopes}")
    result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        return result["access_token"]
    else:
        print(result)
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))
        return None

def get_notebook_id(access_token, notebook_name):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{GRAPH_API_ENDPOINT}/me/onenote/notebooks"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        notebooks = response.json().get("value", [])
        for notebook in notebooks:
            if notebook["displayName"] == notebook_name:
                return notebook["id"]
        print(f"Notebook '{notebook_name}' not found.")
        return None
    else:
      print(f"Error getting notebooks: {response.status_code} - {response.text}")
      return None

def list_sections_and_pages(access_token, notebook_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{GRAPH_API_ENDPOINT}/me/onenote/notebooks/{notebook_id}/sections?$expand=pages"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        sections = response.json().get("value", [])
        for section in sections:
            print(f"Section: {section['displayName']}")
            pages = section.get("pages", [])
            if pages:
                print("  Pages:")
                for page in pages:
                    print(f"    - {page['title']}")
            else:
                print("  No pages in this section.")
        return True
    else:
        print(f"Error getting sections and pages: {response.status_code} - {response.text}")
        return False


if __name__ == "__main__":
    config = get_config()
    if config:
        access_token = get_access_token(config)
        if access_token:
            notebook_id = get_notebook_id(access_token, "Test") # Replace "Test" with your notebook name
            if notebook_id:
                list_sections_and_pages(access_token, notebook_id)
        else:
            print("Failed to acquire access token.")
    else:
        print("Configuration could not be loaded")