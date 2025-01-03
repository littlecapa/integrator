import logging
import os

from integrator.integrator.logging_config import configure_logging
from integrator.integrator.OneDriveLib import OneDriveLib
from integrator.integrator.OneDriveTokenManager import OneDriveTokenManager
from integrator.integrator.OneLib import extract_folder_id, get_id_from_dict
from integrator.integrator.OneNoteLib import OneNoteLib
from integrator.integrator.testlib import get_default_config_path

# Configure logging
configure_logging()
logging.getLogger().setLevel(logging.INFO)

def test_onedrive_operations():
    try:
        token_manager = OneDriveTokenManager(get_default_config_path())
        access_token = token_manager.get_access_token()
      
        if not access_token:
                logging.error("Failed to acquire access token.")
                return
        
        print(f"Access Token: {access_token}")
        
        onenote = OneNoteLib()
        nb_dict = onenote.get_notebooks(access_token)
        nb_id = get_id_from_dict(nb_dict, "Test")
        nb_sections = onenote.list_sections(access_token, nb_id)    
        print(f"Sections in 'Test': {nb_sections}")
        section_id = get_id_from_dict(nb_sections, "Section 1")
        print(f"Section ID: {section_id}")
        pages = onenote.list_pages(access_token, section_id = None)
        print(f"Pages in 'Section 1': {pages}")
        pages = onenote.list_pages(access_token, section_id)
        print(f"Pages in 'Section 1': {pages}")
        page_id = get_id_from_dict(pages, "Page 1")
        print(f"Page ID: {page_id}")


    except Exception as e:
        logging.error(f"An error occurred during the test: {e}", exc_info=True)

if __name__ == "__main__":
    test_onedrive_operations()
