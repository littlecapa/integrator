import logging
import os

from integrator.integrator.logging_config import configure_logging
from integrator.integrator.OneDriveLib import OneDriveLib
from integrator.integrator.OneDriveTokenManager import OneDriveTokenManager
from integrator.integrator.testlib import (get_default_config_path,
                                           get_default_testfile_folder)

# Configure logging
configure_logging()
logging.getLogger().setLevel(logging.INFO)

def test_onedrive_operations():
    # Setup
    token_manager = OneDriveTokenManager(get_default_config_path())

    try:
        access_token = token_manager.get_access_token()
        if not access_token:
            logging.error("Failed to acquire access token.")
            return

        od_folder_name = "TestFolder"
        file_name = "scalable.txt"

        # Initialize OneDriveLib
        onedrive = OneDriveLib()

        # Test: Create directory
        folder_data = onedrive.create_directory(access_token, od_folder_name)
        if not folder_data:
            logging.error(f"Directory creation failed for folder '{od_folder_name}'.")
            return
        folder_id = folder_data["id"]
        logging.info("OneDrive Folder created successfully.")

        # Test: Upload file
        upload_result = onedrive.upload_file_to_directory(access_token, folder_id, get_default_testfile_folder(), file_name)
        if not upload_result:
            logging.error(f"File upload failed for file '{file_name}' in folder '{get_default_testfile_folder()}'.")
            return
        logging.info("File Upload successfully.")
        # Test: Download file
        download_destination = os.path.join(get_default_testfile_folder(), "DownloadedFiles")
        os.makedirs(download_destination, exist_ok=True)
        logging.info("Download Folder created successfully.")
        onedrive.download_file(access_token, folder_id, download_destination, file_name)
        logging.info("File downloaded successfully.")
        # Test: Delete folder and contents
        onedrive.delete_folder_and_contents(access_token, folder_id)

        logging.info("All OneDrive operations completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the test: {e}", exc_info=True)

if __name__ == "__main__":
    test_onedrive_operations()
