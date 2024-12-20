import msal

CLIENT_ID = "6ddd40b2-31e7-4cdb-a3d5-851c62d75b8a"
CLIENT_SECRET = "4Ir8Q~4fHiIx6IHIVyvTzPkgHkSXNL0DGSyaObRX"
AUTHORITY = "https://login.microsoftonline.com/common"  # Common for personal accounts
REDIRECT_URI = "http://localhost"  # Same as the registered URI
SCOPES = ["Files.ReadWrite.All"]

class OneDriveTokenManager:
    def __init__(self, client_id = CLIENT_ID, authority = AUTHORITY, scopes = SCOPES):
        self.app = msal.PublicClientApplication(client_id, authority=authority)
        self.scopes = scopes

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