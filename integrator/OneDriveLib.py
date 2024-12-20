import os

import requests

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
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"Directory '{folder_name}' created successfully.")
            return response.json()
        else:
            print(f"Error creating directory: {response.status_code}, {response.text}")
            return None

    @staticmethod
    def upload_file_to_directory(access_token, folder_id, file_path, file_name):
        url = OneDriveLib.get_file_url(folder_id, file_name)
        headers = {"Authorization": f"Bearer {access_token}"}
        with open(os.path.join(file_path, file_name), "rb") as file_data:
            response = requests.put(url, data=file_data, headers=headers)
        if response.status_code == 201:
            print(f"File '{file_name}' uploaded successfully.")
            return response.json()
        else:
            print(f"Error uploading file: {response.status_code}, {response.text}")
            return None

    @staticmethod
    def download_file(access_token, folder_id, destination_path, file_name):
        url = OneDriveLib.get_file_url(folder_id, file_name)
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(os.path.join(destination_path, file_name), "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded successfully to {destination_path}.")
        else:
            print(f"Error downloading file: {response.status_code}, {response.text}")

    @staticmethod
    def delete_folder_and_contents(access_token, folder_id):
        url = OneDriveLib.get_folder_url(folder_id) + "/children"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            files = response.json().get("value", [])
            for file in files:
                file_id = file["id"]
                file_name = file["name"]
                OneDriveLib.delete_file(access_token, file_id, file_name)
            OneDriveLib.delete_folder(access_token, folder_id)
        else:
            print(f"Error fetching folder contents: {response.status_code}, {response.text}")

    @staticmethod
    def delete_file(access_token, file_id, file_name):
        url = f"{BASE_URL}items/{file_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"File '{file_name}' deleted successfully.")
        else:
            print(f"Error deleting file '{file_name}': {response.status_code}, {response.text}")

    @staticmethod
    def delete_folder(access_token, folder_id):
        url = OneDriveLib.get_folder_url(folder_id)
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print("Folder deleted successfully.")
        else:
            print(f"Error deleting folder: {response.status_code}, {response.text}")
