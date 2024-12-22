import json
import logging
from typing import Optional

import msal

from integrator.integrator.logging_config import log_operation


class OneDriveTokenManager:
    def load_secrets(self, file_path: str) -> None:
        """
        Load client secrets from a JSON configuration file.
        
        Args:
            file_path (str): Path to the configuration file.
            
        Raises:
            ValueError: If required secrets are missing.
            Exception: For unexpected errors during file reading or parsing.
        """
        try:
            with open(file_path, "r") as file:
                secrets = json.load(file)
                self.client_id = secrets.get("CLIENT_ID")
                self.authority = secrets.get("AUTHORITY")
                self.scopes = secrets.get("SCOPES", [])  # Default to an empty list if SCOPES is missing
                self.base_folder_url = secrets.get("BASE_FOLDER_URL")

                # Log the loading operation
                log_operation(
                    "info",
                    f"Secrets loaded from {file_path}.",
                    operation="load_secrets",
                    object=file_path,
                )

                if not self.client_id or not self.authority or not self.scopes or not self.base_folder_url:
                    raise ValueError("Missing required secrets: CLIENT_ID, AUTHORITY, or SCOPES.")
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log_operation(
                "error",
                f"Failed to load secrets from {file_path}: {str(e)}",
                operation="load_secrets",
                object=file_path,
            )
            raise
        except Exception as e:
            log_operation(
                "error",
                f"Unexpected error in load_secrets: {str(e)}",
                operation="load_secrets",
                object=file_path,
            )
            raise

    def __init__(self, config_file_path: str):
        """
        Initialize the OneDriveTokenManager with the given configuration file.

        Args:
            config_file_path (str): Path to the configuration file.
            
        Raises:
            Exception: If initialization fails due to errors in loading secrets or MSAL setup.
        """
        try:
            self.load_secrets(config_file_path)
            self.app = msal.PublicClientApplication(self.client_id, authority=self.authority)
            log_operation(
                "info",
                "Token manager initialized.",
                operation="init_token_manager",
                object=config_file_path,
            )
        except Exception as e:
            log_operation(
                "error",
                f"Initialization failed: {str(e)}",
                operation="init_token_manager",
                object=config_file_path,
            )
            raise

    def get_base_folder_url(self) -> Optional[str]:
        """
        Get the base folder URL for OneDrive operations.

        Returns:
            Optional[str]: Base folder URL or None if not set.
        """
        return self.base_folder_url

    def acquire_token_silent(self) -> Optional[dict]:
        """
        Attempt to acquire a token silently using cached credentials.

        Returns:
            Optional[dict]: Token result or None if no accounts are available.
        """
        accounts = self.app.get_accounts()
        if accounts:
            return self.app.acquire_token_silent(self.scopes, account=accounts[0])
        return None

    def acquire_token_interactive(self) -> dict:
        """
        Prompt the user to log in interactively to acquire a token.

        Returns:
            dict: Token result from interactive login.
        """
        log_operation(
            "info",
            "Prompting user for interactive login.",
            operation="get_access_token",
        )
        return self.app.acquire_token_interactive(self.scopes)

    def get_access_token(self) -> Optional[str]:
        """
        Obtain an access token, falling back to interactive login if necessary.

        Returns:
            Optional[str]: Access token or None if token acquisition fails.
        """
        try:
            result = self.acquire_token_silent()
            if not result:
                result = self.acquire_token_interactive()

            if "access_token" in result:
                log_operation(
                    "info",
                    "Access token acquired successfully.",
                    operation="get_access_token",
                )
                return result["access_token"]
            else:
                log_operation(
                    "error",
                    f"Failed to acquire access token: {result.get('error_description', 'Unknown error')}",
                    operation="get_access_token",
                )
                return None
        except Exception as e:
            log_operation(
                "error",
                f"Unexpected error during token acquisition: {str(e)}",
                operation="get_access_token",
            )
            return None
