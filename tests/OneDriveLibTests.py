import os

from integrator.integrator.OneDriveLib import OneDriveLib
from integrator.integrator.OneDriveTokenManager import OneDriveTokenManager

if __name__ == "__main__":
    file_path = "/Users/littlecapa/Downloads"
    token_manager = OneDriveTokenManager(os.path.join(file_path, "OneDriveConfig.json"))
    access_token = token_manager.get_access_token()
    if access_token:
        folder_name = "TestFolder"
        folder_data = OneDriveLib.create_directory(access_token, folder_name)
        if folder_data:
            folder_id = folder_data["id"]

            
            file_name = "scalable.txt"
            OneDriveLib.upload_file_to_directory(access_token, folder_id, file_path, file_name)

            OneDriveLib.download_file(access_token, folder_data["id"], file_path, file_name)
            OneDriveLib.delete_folder_and_contents(access_token, folder_id)