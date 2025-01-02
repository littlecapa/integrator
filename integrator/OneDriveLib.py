import os

import requests

from integrator.integrator.logging_config import log_operation
from integrator.integrator.OneLib import (get_headers, is_notebook,
                                          list_all_attributes)


class OneDriveLib:
    def __init__(self, base_url: str = "https://graph.microsoft.com/v1.0/me/drive/"):
        """
        Initialize the OneDriveLib instance with a base URL.

        Args:
            base_url (str): The base URL for OneDrive API. Defaults to Microsoft Graph API endpoint for OneDrive.
        """
        self.base_url = base_url

    def get_file_url(self, folder_id: str, file_name: str) -> str:
        """
        Generate the URL to access a file in a folder.
        """
        return f"{self.base_url}items/{folder_id}:/{file_name}:/content"

    def get_folder_url(self, folder_id: str) -> str:
        """
        Generate the URL to access a folder.
        """
        return f"{self.base_url}items/{folder_id}"
    
    def list_root_objects(self, access_token: str) -> list:
        """List all objects in the OneDrive root folder."""
        url = f"{self.base_url}/root/children"
        try:
            response = requests.get(url, headers=get_headers(access_token))
            response.raise_for_status()
            return response.json().get("value", [])
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error fetching folder contents for ROOT Folder: {str(e)}",
                operation="list_root_objects",
            ) 
            return []

    def find_onenote_notebook(self, access_token, notebook_name: str):
        """Find a OneNote notebook in the root folder by name."""
        objects = self.list_root_objects(access_token)
        for obj in objects:
            log_operation(
                    "info",
                    f"Object found: {obj.get('name')} (ID: {obj.get('id')})",
                    operation="find_onenote_notebook",
                    object=notebook_name,
                )
            if obj.get("name") == notebook_name and is_notebook(obj):
                log_operation(
                    "info",
                    f"Found Notebook: {notebook_name} (ID: {obj.get('id')} {list_all_attributes(obj)})",
                    operation="find_onenote_notebook",
                    object=notebook_name,
                )
                return obj
        return None

    def get_folder_content(self, access_token: str, folder_id: str) -> dict:
        """
        Fetch the contents of a folder from OneDrive.

        Args:
            access_token (str): The access token for authentication.
            folder_id (str): The ID of the folder.

        Returns:
            dict: The contents of the folder.
        """
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
        try:
            response = requests.get(url, headers=get_headers(access_token))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error fetching folder contents for ID {folder_id}: {str(e)}",
                operation="get_folder_contents",
                object=folder_id,
            )
            return None

    def get_folders(self, access_token: str, base_url: str = None) -> dict:
        """
        Recursively fetch all folders and subfolders in OneDrive starting from the base URL.
        
        Args:
            access_token (str): Access token for authorization.
            base_url (str): Base URL to start fetching folders. Defaults to the root directory.

        Returns:
            dict: A nested dictionary representing the folder structure.
        """
        log_operation(
                "info",
                f"Start Folder: (URL: {base_url})",
                operation="check directory",
                object=base_url,
            )
        base_url = base_url or self.base_url + "root/children"

        folder_structure = {}

        try:
            response = requests.get(base_url, headers=get_headers(access_token))
            response.raise_for_status()
            items = response.json().get("value", [])
            
            for item in items:
                if item.get("folder"):  # Check if the item is a folder
                    folder_name = item["name"]
                    folder_url = self.get_folder_url(item["id"])
                    log_operation(
                            "info",
                            f"Found Folder: {folder_name} (URL: {folder_url})",
                            operation="found subdirectory",
                            object=f"Name: {folder_name}, ID: {folder_url}",
                        )
                    folder_structure[folder_name] = {
                        "FolderURL": folder_url,
                        "Subfolders": self.get_folders(access_token, folder_url + "/children"),
                    }
                else:
                    log_operation(
                            "info",
                            f"No Folder: {item})",
                            operation="found subdirectory",
                            object=f"item: {item}",
                        )
            return folder_structure
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error fetching folders: {str(e)}",
                operation="get_folders",
            )
            return {}

    def create_directory(self, access_token: str, folder_name: str) -> dict:
        """
        Create a new directory in the root of OneDrive.
        """
        url = f"{self.base_url}root/children"
        
        data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename",
        }
        try:
            response = requests.post(url, json=data, headers=get_headers(access_token))
            response.raise_for_status()
            folder_id = response.json().get("id")
            log_operation(
                "info",
                f"Directory created: {folder_name} (ID: {folder_id})",
                operation="create_directory",
                object=folder_name,
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error creating directory '{folder_name}': {str(e)}",
                operation="create_directory",
                object=folder_name,
            )
            return None

    def upload_file_to_directory(self, access_token: str, folder_id: str, file_path: str, file_name: str) -> dict:
        """
        Upload a file to a specific directory in OneDrive.
        """
        if not os.path.isfile(os.path.join(file_path, file_name)):
            log_operation(
                "error",
                f"File not found: {os.path.join(file_path, file_name)}",
                operation="upload_file",
                object=file_path,
            )
            return None

        url = self.get_file_url(folder_id, file_name)
        
        try:
            with open(os.path.join(file_path, file_name), "rb") as file_data:
                response = requests.put(url, data=file_data, headers=get_headers(access_token))
            response.raise_for_status()
            file_id = response.json().get("id")
            log_operation(
                "info",
                f"File uploaded: {file_name} to folder {folder_id} (ID: {file_id})",
                operation="upload_file",
                object=file_name,
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error uploading file '{file_name}': {str(e)}",
                operation="upload_file",
                object=file_name,
            )
            return None

    def download_file(self, access_token: str, folder_id: str, destination_path: str, file_name: str) -> None:
        """
        Download a file from OneDrive to the specified destination.
        """
        url = self.get_file_url(folder_id, file_name)
        
        try:
            response = requests.get(url, headers=get_headers(access_token), stream=True)
            response.raise_for_status()
            with open(os.path.join(destination_path, file_name), "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            log_operation(
                "info",
                f"File downloaded: {file_name} to {destination_path}",
                operation="download_file",
                object=file_name,
            )
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error downloading file '{file_name}': {str(e)}",
                operation="download_file",
                object=file_name,
            )

    def delete_folder_and_contents(self, access_token: str, folder_id: str) -> None:
        """
        Delete a folder and all its contents from OneDrive.
        """
        url = self.get_folder_url(folder_id) + "/children"
        
        try:
            response = requests.get(url, headers=get_headers(access_token))
            response.raise_for_status()
            files = response.json().get("value", [])
            for file in files:
                file_id = file["id"]
                file_name = file["name"]
                self.delete_file(access_token, file_id, file_name)
            self.delete_folder(access_token, folder_id)
            log_operation(
                "info",
                f"Folder and its contents deleted: {folder_id}",
                operation="delete_folder_and_contents",
                object=folder_id,
            )
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error deleting folder contents for '{folder_id}': {str(e)}",
                operation="delete_folder_and_contents",
                object=folder_id,
            )

    def delete_file(self, access_token: str, file_id: str, file_name: str) -> None:
        """
        Delete a file from OneDrive.
        """
        url = f"{self.base_url}items/{file_id}"
        
        try:
            response = requests.delete(url, headers=get_headers(access_token))
            response.raise_for_status()
            log_operation(
                "info",
                f"File deleted: {file_name} (ID: {file_id})",
                operation="delete_file",
                object=file_name,
            )
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error deleting file '{file_name}': {str(e)}",
                operation="delete_file",
                object=file_name,
            )

    def delete_folder(self, access_token: str, folder_id: str) -> None:
        """
        Delete a folder from OneDrive.
        """
        url = self.get_folder_url(folder_id)
        
        try:
            response = requests.delete(url, headers=get_headers(access_token))
            response.raise_for_status()
            log_operation(
                "info",
                f"Folder deleted: {folder_id}",
                operation="delete_folder",
                object=folder_id,
            )
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error deleting folder '{folder_id}': {str(e)}",
                operation="delete_folder",
                object=folder_id,
            )
