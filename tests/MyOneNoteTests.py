import logging

from integrator.integrator.logging_config import (configure_logging,
                                                  log_operation)
from integrator.integrator.MyOneNote_Lib import MyOneNote_Lib

# Configure logging
configure_logging()
logging.getLogger().setLevel(logging.INFO)

def test_onenote_lib():
    try:
        # Initialize MyOneNote_Lib
        onenote_lib = MyOneNote_Lib()

        # Fetch notebooks
        notebooks = onenote_lib.get_notebooks()
        if not notebooks:
            log_operation("info", "No notebooks found.", operation="test_onenote_lib")
            return

        # Assuming the first notebook is "Test" (you can modify the logic here to find it by name)
        notebook_name = "Test"
        notebook = next((nb for nb in notebooks if nb["name"] == notebook_name), None)

        if not notebook:
            log_operation("info", f"Notebook '{notebook_name}' not found.", operation="test_onenote_lib")
            return

        print(f"Found Notebook: {notebook_name}")

        # Fetch sections from the found notebook
        sections = onenote_lib.get_sections(notebook["id"])
        if not sections:
            log_operation("info", f"No sections found for notebook '{notebook_name}'.", operation="test_onenote_lib")
            return

        # Assuming the first section is "Section 1" (you can modify this to find it by name)
        section_name = "Section 2"
        section = next((sec for sec in sections if sec["name"] == section_name), None)

        if not section:
            log_operation("info", f"Section '{section_name}' not found in notebook '{notebook_name}'.", operation="test_onenote_lib")
            return

        print(f"Found Section: {section_name}")

        # Fetch pages from the found section
        pages = onenote_lib.get_pages(section["id"])
        if not pages:
            log_operation("info", f"No pages found in section '{section_name}'.", operation="test_onenote_lib")
            return

        # Display pages
        print(f"Pages in Section '{section_name}':")
        for page in pages:
            print(f"- {page['title']}")

    except Exception as e:
        log_operation("error", f"An error occurred: {str(e)}", operation="test_onenote_lib")

if __name__ == "__main__":
    test_onenote_lib()
