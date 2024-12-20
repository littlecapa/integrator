import logging
import os

from integrator.integrator.logging_config import configure_logging
from integrator.integrator.OneDriveLib import OneDriveLib
from integrator.integrator.OneDriveTokenManager import OneDriveTokenManager

# Configure logging
configure_logging()
logging.getLogger().setLevel(logging.INFO)

def test_onedrive_operations():
    # Setup
    file_path = os.getenv("TEST_FILE_PATH", "/Users/littlecapa/Downloads")
    config_path = os.path.join(file_path, "OneDriveConfig.json")
    token_manager = OneDriveTokenManager(config_path)

    try:
        access_token = token_manager.get_access_token()
        if not access_token:
            logging.error("Failed to acquire access token.")
            return

        folder_name = "TestFolder"
        file_name = "scalable.txt"

        # Test: Create directory
        folder_data = OneDriveLib.create_directory(access_token, folder_name)
        if not folder_data:
            logging.error("Directory creation failed.")
            return

        folder_id = folder_data["id"]

        # Test: Upload file
        upload_result = OneDriveLib.upload_file_to_directory(access_token, folder_id, file_path, file_name)
        if not upload_result:
            logging.error("File upload failed.")
            return

        # Test: Download file
        OneDriveLib.download_file(access_token, folder_id, file_path, file_name)

        # Test: Delete folder and contents
        OneDriveLib.delete_folder_and_contents(access_token, folder_id)

        logging.info("All OneDrive operations completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the test: {e}", exc_info=True)

if __name__ == "__main__":
    test_onedrive_operations()
