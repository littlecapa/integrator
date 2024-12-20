import json

import msal


class OneDriveTokenManager:

    def load_secrets(self, file_path):
        with open(file_path, "r") as file:
            secrets = json.load(file)
            self.client_id = secrets["CLIENT_ID"]
            #self.CLIENT_SECRET = secrets["CLIENT_SECRET"]
            self.authority = secrets["AUTHORITY"]
            #self.REDIRECT_URI = secrets["REDIRECT_URI"]
            self.scopes = secrets["SCOPES"]
        
    def __init__(self, config_file_path):
        self.load_secrets(config_file_path)
        self.app = msal.PublicClientApplication(self.client_id, authority=self.authority)

    def get_access_token(self):
        result = None
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
        if not result:
            print("Please log in to acquire a token.")
            result = self.app.acquire_token_interactive(self.scopes)

        if "access_token" in result:
            return result["access_token"]
        else:
            print("Error: ", result.get("error_description"))
            return None