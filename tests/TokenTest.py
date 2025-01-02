import logging
import os

import jwt

from integrator.integrator.logging_config import configure_logging
from integrator.integrator.OneDriveLib import OneDriveLib
from integrator.integrator.OneDriveTokenManager import OneDriveTokenManager
from integrator.integrator.OneLib import extract_folder_id, get_id_from_dict
from integrator.integrator.OneNoteLib import OneNoteLib
from integrator.integrator.testlib import get_default_config_path

# Configure logging
configure_logging()
logging.getLogger().setLevel(logging.INFO)

def test_token():
    try:
        token_manager = OneDriveTokenManager(get_default_config_path())
        access_token = token_manager.get_access_token()
      
        if not access_token:
                logging.error("Failed to acquire access token.")
                return
        
        print(f"Access Token: {access_token}")
        if "." not in access_token:
            print("This token is not a valid JWT:", access_token)
        else:
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            print(decoded_token)
    except Exception as e:
        logging.error(f"An error occurred during the test: {e}", exc_info=True)

if __name__ == "__main__":
    test_token()
