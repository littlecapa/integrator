import os

import requests

from integrator.integrator.logging_config import log_operation

BASE_URL = "https://graph.microsoft.com/v1.0/me/drive/"

class OneDriveLib:
    @staticmethod
    def get_file_url(folder_id, file_name):
        return f"{BASE_URL}items/{folder_id}:/{file_name}:/content"

    @staticmethod
    def get_folder_url(folder_id):
        return f"{BASE_URL}items/{folder_id}"

    @staticmethod
    def create_directory(access_token, folder_name):
        url = f"{BASE_URL}root/children"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            log_operation("info", f"Directory created: {folder_name} with ID {response.json()['id']}")
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation("error", f"Error creating directory: {str(e)}", operation="create_directory")
            return None

    @staticmethod
    def upload_file_to_directory(access_token, folder_id, file_path, file_name):
        if not os.path.exists(file_path):
            log_operation("error", f"File path not found: {file_path}", operation="upload_file")
            return None

        url = OneDriveLib.get_file_url(folder_id, file_name)
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            with open(os.path.join(file_path, file_name), "rb") as file_data:
                response = requests.put(url, data=file_data, headers=headers)
            response.raise_for_status()
            log_operation("info", f"File uploaded: {file_name} to folder {folder_id}")
    
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation("error", f"Error uploading file: {str(e)}", operation="upload_file")
            return None

    @staticmethod
    def download_file(access_token, folder_id, destination_path, file_name):
        url = OneDriveLib.get_file_url(folder_id, file_name)
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            with open(os.path.join(destination_path, file_name), "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            log_operation("info", f"File downloaded: {file_name} to {destination_path}")
        except requests.exceptions.RequestException as e:
            log_operation("error", f"Error downloading file: {str(e)}", operation="download_file")

    @staticmethod
    def delete_folder_and_contents(access_token, folder_id):
        url = OneDriveLib.get_folder_url(folder_id) + "/children"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            files = response.json().get("value", [])
            for file in files:
                file_id = file["id"]
                file_name = file["name"]
                OneDriveLib.delete_file(access_token, file_id, file_name)
            OneDriveLib.delete_folder(access_token, folder_id)
            log_operation("info", f"Folder and contents deleted: {folder_id}")
        except requests.exceptions.RequestException as e:
            log_operation("error", f"Error fetching folder contents: {str(e)}", operation="delete_folder_and_contents")

    @staticmethod
    def delete_file(access_token, file_id, file_name):
        url = f"{BASE_URL}items/{file_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            log_operation("info", f"File deleted: {file_name}")
        except requests.exceptions.RequestException as e:
            log_operation("error", f"Error deleting file '{file_name}': {str(e)}", operation="delete_file")

    @staticmethod
    def delete_folder(access_token, folder_id):
        url = OneDriveLib.get_folder_url(folder_id)
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            log_operation("info", f"Folder deleted: {folder_id}")
        except requests.exceptions.RequestException as e:
            log_operation("error", f"Error deleting folder: {str(e)}", operation="delete_folder")
