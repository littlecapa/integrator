import logging
import os

from integrator.integrator.logging_config import configure_logging
from integrator.integrator.OneDriveTokenManager import OneDriveTokenManager
from integrator.integrator.OneLib import extract_folder_id
from integrator.integrator.OneNoteLib import OneNoteLib
from integrator.integrator.testlib import get_default_config_path

# Configure logging
configure_logging()
logging.getLogger().setLevel(logging.INFO)

def test_onedrive_operations():
    # Setup
    token_manager = OneDriveTokenManager(get_default_config_path())
    base_folder_id = extract_folder_id(token_manager.get_base_folder_url())
    onenote = OneNoteLib(base_folder_id)

    try:
        access_token = token_manager.get_access_token()
        if not access_token:
            logging.error("Failed to acquire access token.")
            return

        # Get the list of notebooks
        notebooks = onenote.get_notebooks(access_token)
        print("Notebooks:", notebooks)

    except Exception as e:
        logging.error(f"An error occurred during the test: {e}", exc_info=True)

if __name__ == "__main__":
    test_onedrive_operations()
