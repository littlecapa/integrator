import logging
import os

from integrator.integrator.logging_config import configure_logging
from integrator.integrator.OneDriveLib import OneDriveLib
from integrator.integrator.OneDriveTokenManager import OneDriveTokenManager
from integrator.integrator.OneLib import extract_folder_id
from integrator.integrator.OneNoteLib import OneNoteLib
from integrator.integrator.testlib import get_default_config_path

# Configure logging
configure_logging()
logging.getLogger().setLevel(logging.INFO)

def test_onelib_helloworld():
    try:
        token_manager = OneDriveTokenManager(get_default_config_path())
        access_token = token_manager.get_access_token()
        if not access_token:
                logging.error("Failed to acquire access token.")
                return
        notebook_name = "Test"
        print(f"Access Token: {access_token}")

        onedrive = OneDriveLib()
        notebook = onedrive.find_onenote_notebook(access_token=access_token, notebook_name=notebook_name)
        if not notebook:
            print(f"Notebook '{notebook_name}' not found.")
            return
        print("Notebook found")
            
        onenote = OneNoteLib()

        notebook_id = notebook["id"]
    
        sections = onenote.list_sections(access_token, notebook_id)
        if not sections:
            print(f"No sections found in notebook '{notebook_name}'.")
            return

        print(f"Sections in '{notebook_name}':")
        for section in sections:
            print(f" - {section['displayName']} (ID: {section['id']})")

            # Step 3: List all pages in the section
            pages = onenote.list_pages(access_token, section["id"])
            for page in pages:
                print(f"   * Page: {page['title']} (ID: {page['id']})")

    except Exception as e:
        logging.error(f"An error occurred during the test: {e}", exc_info=True)

if __name__ == "__main__":
    test_onelib_helloworld()
