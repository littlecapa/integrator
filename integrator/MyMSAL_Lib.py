import json

import msal
import requests

from integrator.integrator.logging_config import log_operation


class MyMSAL_Lib:
    def __init__(self, config):
        """
        Initialize the MSAL client application and acquire an access token.
        """
        
        try:
            self.config = config
            self.app = msal.PublicClientApplication(
                client_id=config['CLIENT_ID'],
                authority=config['AUTHORITY']
            )
            if "access_token" in config and config["access_token"]:
                self.access_token = config["access_token"]
            else:
                self.access_token = None
                self.acquire_access_token()
            print(f"Access:Token: #{self.access_token}#")
        except Exception as e:
            log_operation(
                "error",
                f"Failed to initialize MyMSAL_Lib: {str(e)}",
                operation="init_msal_lib"
            )

    def acquire_access_token(self):
        """
        Acquire an access token interactively.
        """
        try:
            result = self.app.acquire_token_interactive(
                scopes=self.config['SCOPES']
            )
            if "access_token" in result:
                self.access_token = result["access_token"]
            else:
                log_operation(
                    "error",
                    f"Failed to acquire access token: {result.get('error_description', 'Unknown error')}",
                    operation="acquire_access_token"
                )
        except Exception as e:
            log_operation(
                "error",
                f"Unexpected error during token acquisition: {str(e)}",
                operation="acquire_access_token"
            )

    def get_request(self, request_url):
        """
        Send a GET request to the provided URL using the stored access token.
        """
        url = f"{self.config['GRAPH_API_BASE_URL']}{request_url}"
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Get Request failed for URL {url}: {str(e)}",
                operation="get_request",
                object=url
            )
            return None
        
    def post_request(self, request_url, headers={}, data=None):
        """
        Send a GET request to the provided URL using the stored access token.
        """
        url = f"{self.config['GRAPH_API_BASE_URL']}{request_url}"
        try:
            headers["Authorization"] = f"Bearer {self.access_token}"
            print(f"Headers: {headers}")
            if data:
                # If the data is not already a JSON string, convert it
                if isinstance(data, dict):
                    data = json.dumps(data)
                    headers["Content-Type"] = "application/json"  # Ensure content type is set to JSON

            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Post Request failed for URL {url} Headers {headers} Data {data}: {str(e)}",
                operation="post_request",
                object=url
            )