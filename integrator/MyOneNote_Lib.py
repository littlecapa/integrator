from integrator.integrator.logging_config import log_operation
from integrator.integrator.MyMSAL_Lib import MyMSAL_Lib


class DefaultConfig:
    CLIENT_ID = "84ff9f0b-8484-4cf3-a033-d68d325a0254"
    AUTHORITY = "https://login.microsoftonline.com/common"
    #AUTHORITY = "https://login.microsoftonline.com/74f33026-382b-40ba-ad76-8cbb5346bb03"
    SCOPES = [
        "Notes.ReadWrite.All",
        "Notes.Read.All",
        "Notes.Create",
        "User.Read"
    ]
    GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"
    GRAPH_API_BASE_URL_BETA = "https://graph.microsoft.com/beta"

class DefaultEndpoints:
    NOTEBOOKS = "/me/onenote/notebooks"
    SECTIONS = "/me/onenote/notebooks/{notebook-id}/sections"
    PAGES = "/me/onenote/sections/{section-id}/pages"
    PAGE = "/me/onenote/pages/{page-id}"

class MyOneNote_Lib:
    def __init__(self, msal_config = None, endpoints = None):
        """
        Initialize the MyOneNote_Lib with a MyMSAL_Lib object.
        """
        if msal_config is None:
            msal_config = DefaultConfig.__dict__
        if endpoints is None:
            endpoints = DefaultEndpoints.__dict__
        try:
            self.endpoints = endpoints  
            self.msal_lib = MyMSAL_Lib(msal_config)
        except Exception as e:
            log_operation(
                "error",
                f"Failed to initialize MyOneNote_Lib: {str(e)}",
                operation="init_onenote_lib"
            )

    def get_notebooks(self):
        """
        Get a list of notebook names and IDs.
        """
        try:
            url = self.endpoints["NOTEBOOKS"]
            response = self.msal_lib.get_request(url)
            if response:
                return [
                    {"name": notebook["displayName"], "id": notebook["id"]}
                    for notebook in response.get("value", [])
                ]
            return []
        except Exception as e:
            log_operation(
                "error",
                f"Failed to get notebooks: {str(e)}",
                operation="get_notebooks"
            )
            return []

    def get_sections(self, notebook_id):
        """
        Get a list of sections for a given notebook ID.
        """
        try:
            url = self.endpoints["SECTIONS"].replace("{notebook-id}", notebook_id)
            response = self.msal_lib.get_request(url)
            if response:
                print(f"Response: {response}")
                return [
                    {"name": section["displayName"], "id": section["id"]}
                    for section in response.get("value", [])
                ]
            return []
        except Exception as e:
            log_operation(
                "error",
                f"Failed to get sections for notebook '{notebook_id}': {str(e)}",
                operation="get_sections",
                object=notebook_id
            )
            return []

    def get_pages(self, section_id):
        """
        Get a list of pages for a given section ID.
        """
        try:
            url = self.endpoints["PAGES"].replace("{section-id}", section_id)
            response = self.msal_lib.get_request(url)
            if response:
                return [
                    {"title": page["title"], "id": page["id"]}
                    for page in response.get("value", [])
                ]
            return []
        except Exception as e:
            log_operation(
                "error",
                f"Failed to get pages for section '{section_id}': {str(e)}",
                operation="get_pages",
                object=section_id
            )
            return []
        
    def get_page(self, page_id):
        """
        Get a list of pages for a given section ID.
        """
        try:
            url = self.endpoints["PAGE"].replace("{page-id}", page_id)
            response = self.msal_lib.get_request(url)
            if response:
                return [
                    {"title": page["title"], "id": page["id"]}
                    for page in response.get("value", [])
                ]
            return []
        except Exception as e:
            log_operation(
                "error",
                f"Failed to get page for id '{page_id}': {str(e)}",
                operation="get_page",
                object=page_id
            )
            return []
        
    def create_section(self, notebook_id, section_name):
        """
        Create a new section in a notebook.
        """
        url = self.endpoints["SECTIONS"].replace("{notebook-id}", notebook_id)
        payload = {"displayName": section_name}
        response = self.msal_lib.post_request(url, data=payload)
        if response:
            section_id = response.get('id')  # Assuming the response contains an 'id' field for the section
            return section_id
        else:
            # Handle failure
            log_operation("error", f"Failed to create section for notebook {notebook_id}", operation="create_section")
            return None

    def create_page(self, section_id, title, content):
        """
        Create a new page with HTML content in a section.
        """
        url = self.endpoints["PAGES"].replace("{section-id}", section_id)
        headers = {"Content-Type": "application/xhtml+xml"}
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        
        response = self.msal_lib.post_request(url, headers=headers, data=html)
        print(f"Response Page Created: {response}")
        if response:
            page_id = response.get('id')  # Assuming the response contains an 'id' field for the page
            return page_id
        else:
            # Handle failure
            log_operation("error", f"Failed to create page in section {section_id}", operation="create_page")
            return None