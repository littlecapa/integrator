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

        new_section = onenote_lib.create_section(notebook["id"], "Section New")
        if not new_section:
            log_operation("info", f"No sections found for notebook '{notebook_name}'.", operation="test_onenote_lib")
            return
        print(f"New Section: {new_section}")

        new_page = onenote_lib.create_page(new_section, title="New Page", content="New Page Content!")
        if not new_page:
            log_operation("info", f"No sections found for section '{new_section}'.", operation="test_onenote_lib")
            return
        print(f"New Page: {new_page}")

        #Fetch New Page
        # Fetch pages from the found section
        page_name, page_content = onenote_lib.get_page(new_page)
        if not page_name:
            log_operation("info", f"No page found for ID '{new_page}'.", operation="test_onenote_lib")
            return
        print(f"Page Name: {page_name} Page Content: {page_content}")

        # Fetch pages from the found section
        pages = onenote_lib.get_pages(new_section)
        if not pages:
            log_operation("info", f"No pages found in section '{new_section}'.", operation="test_onenote_lib")
            return

        # Display pages
        print(f"Pages in Section '{new_section}':")
        for page in pages:
            print(f"- {page['title']}")


    except Exception as e:
        log_operation("error", f"An error occurred: {str(e)}", operation="test_onenote_lib")

if __name__ == "__main__":
    test_onenote_lib()
