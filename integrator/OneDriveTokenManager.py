import json

import msal

from integrator.integrator.logging_config import log_operation


class OneDriveTokenManager:
    def load_secrets(self, file_path):
        try:
            with open(file_path, "r") as file:
                secrets = json.load(file)
                self.client_id = secrets.get("CLIENT_ID")
                self.authority = secrets.get("AUTHORITY")
                self.scopes = secrets.get("SCOPES")
                
                # Log the loading operation even if some secrets are missing
                log_operation("info", f"Secrets loaded from {file_path}.", operation="load_secrets")
                
                # Raise error if any required secret is missing
                if not self.client_id or not self.authority or not self.scopes:
                    raise ValueError("Missing required secrets.")
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log_operation("error", f"Failed to load secrets from {file_path}: {str(e)}", operation="load_secrets")
            raise
        except ValueError as e:
            log_operation("error", f"Error in load_secrets: {str(e)}", operation="load_secrets")
            raise
        except Exception as e:
            log_operation("error", f"Unexpected error in load_secrets: {str(e)}", operation="load_secrets")
            raise

    def __init__(self, config_file_path):
        try:
            self.load_secrets(config_file_path)
            self.app = msal.PublicClientApplication(self.client_id, authority=self.authority)
            log_operation("info", "Token manager initialized.", operation="init token manager")
        except Exception as e:
            log_operation("error", f"Initialization failed: {str(e)}", operation="init token manager")
            raise

    def acquire_token_silent(self):
        accounts = self.app.get_accounts()
        if accounts:
            return self.app.acquire_token_silent(self.scopes, account=accounts[0])
        return None

    def acquire_token_interactive(self):
        log_operation("info", "Prompting user for interactive login.", operation="get_access_token")
        return self.app.acquire_token_interactive(self.scopes)

    def get_access_token(self):
        try:
            result = self.acquire_token_silent()
            if not result:
                result = self.acquire_token_interactive()

            if "access_token" in result:
                log_operation("info", "Access token acquired successfully.", operation="get_access_token")
                return result["access_token"]
            else:
                error_description = result.get("error_description", "Unknown error")
                log_operation("error", f"Failed to acquire access token: {error_description}", operation="get_access_token")
                return None
        except Exception as e:
            log_operation("error", f"Unexpected error during token acquisition: {str(e)}", operation="get_access_token")
            return None
