import os

import requests

from integrator.integrator.logging_config import log_operation
from integrator.integrator.OneLib import get_headers

#
# For Testing the URLs: https://developer.microsoft.com/en-us/graph/graph-explorer?request=me/onenote/pages&version=v1.0
#

# API Base URL for OneNote: https://graph.microsoft.com/v1.0/me/onenote/notebooks

ONENOTE_NOTEBOOK_BASE_URL = "https://graph.microsoft.com/v1.0/me/onenote/notebooks"
ONENOTE_SECTION_BASE_URL = f"https://graph.microsoft.com/v1.0/me/onenote/sections"
ONENOTE_PAGE_BASE_URL = f"https://graph.microsoft.com/v1.0/me/onenote/pages"



class OneNoteLib:
    def __init__(self):
        """
        Initialize the OneNoteLib instance with a base URL.

        Args:
            base_url (str): The base URL for OneNote API. Defaults to Microsoft Graph API endpoint for OneNote.
        """
        self.notebook_base_url = ONENOTE_NOTEBOOK_BASE_URL
        self.section_base_url = ONENOTE_SECTION_BASE_URL
        self.page_base_url = ONENOTE_PAGE_BASE_URL

    def get_notebook_url(self, notebook_id: str) -> str:
        """
        Generate the URL to access a specific notebook.
        """
        return f"{self.notebook_base_url}/{notebook_id}"

    def get_section_url(self, section_id: str) -> str:
        """
        Generate the URL to access a specific section.
        """
        return f"{self.section_base_url}/{section_id}"

    def get_page_url(self, page_id: str) -> str:
        """
        Generate the URL to access a specific page.
        """
        return f"{self.page_base_url}/{page_id}"

    def get_notebooks(self, access_token: str) -> dict:
        """
        Retrieve all notebooks for the authenticated user.
        """
        
        try:
            response = requests.get(self.notebook_base_url, headers=get_headers(access_token), timeout=10)
            response.raise_for_status()
            
            notebooks = response.json()
            if 'value' not in notebooks:
                log_operation(
                    "error",
                    "No 'value' key in API response",
                    operation="get_notebooks",
                    object="notebooks"
                )
                return []

            log_operation(
                "info",
                "Retrieved notebooks successfully",
                operation="get_notebooks",
                object="notebooks"
            )

            notebook_list = [
                {"name": notebook.get('displayName', 'Unnamed'), "id": notebook.get('id')}
                for notebook in notebooks['value']
            ]
            return notebook_list

        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error retrieving notebooks: {str(e)}",
                operation="get_notebooks",
                object="notebooks"
            )
            return []

    def list_sections(self, access_token: str, notebook_id: str) -> list[dict[str, str]]:
        """
        List all sections in a OneNote notebook.

        Args:
            access_token (str): The access token for authentication.
            notebook_id (str): The ID of the OneNote notebook.

        Returns:
            list[dict[str, str]]: A list of sections with their names and IDs.
            Returns an empty list if an error occurs.

        Logs:
            Logs errors to the application's logging mechanism.
        """
        url = f"{self.notebook_base_url}/{notebook_id}/sections"
        try:
            headers = get_headers(access_token) or {}
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Extract and format section information
            sections = response.json().get("value", [])
            section_info = [
                {"name": section.get("displayName", "Unnamed Section"), "id": section.get("id", "")}
                for section in sections
            ]

            log_operation(
                "info",
                f"Successfully retrieved {len(section_info)} sections for notebook '{notebook_id}'.",
                operation="list_sections",
                object=notebook_id,
            )
            return section_info

        except requests.exceptions.RequestException as e:
            error_message = f"Error listing sections for notebook '{notebook_id}': {str(e)}"
            if response is not None:
                error_message += f" (Status Code: {response.status_code}, Response: {response.text})"

            log_operation(
                "error",
                error_message,
                operation="list_sections",
                object=notebook_id,
            )
            return []
        
    def list_pages(self, access_token, section_id: str = None):
        """List all pages in a OneNote section."""
        if section_id is None:
            url = f"{self.page_base_url}"
        else:
            url = f"{self.section_base_url}/{section_id}/pages"

        try:
            response = requests.get(url, headers=get_headers(access_token))
            response.raise_for_status()
            return response.json().get("value", [])
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error listing pages for section '{section_id}': {str(e)}",
                operation="list_pages",
                object=section_id
            )
            return []
   
    def get_notebook_structure(self, access_token: str, notebook_id: str) -> dict:
        """
        Get the structure of a notebook, including sections and pages.
        """
        url = f"{self.notebook_base_url}/{notebook_id}/sections"
        print(url)
        
        try:
            response = requests.get(url, headers=get_headers(access_token))
            print
            response.raise_for_status()
            
            sections = response.json().get("value", [])
            notebook_structure = {}
            for section in sections:
                section_id = section['id']
                section_name = section['displayName']
                pages_url = f"{self.base_url}sections/{section_id}/pages"
                pages_response = requests.get(pages_url, headers=get_headers(access_token))
                pages_response.raise_for_status()
                pages = pages_response.json().get("value", [])
                notebook_structure[section_name] = [
                    {'page_id': page['id'], 'page_title': page['title']} for page in pages
                ]
            log_operation(
                "info",
                f"Structure retrieved for notebook {notebook_id}",
                operation="get_notebook_structure",
                object=notebook_id
            )
            return notebook_structure
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error retrieving structure for notebook '{notebook_id}': {str(e)}",
                operation="get_notebook_structure",
                object=notebook_id
            )
            return None

    def create_page(self, access_token: str, section_id: str, title: str, content_html: str) -> dict:
        """
        Create a page in a specific section of a OneNote notebook.
        """
        url = f"{self.notebook_base_url}sections/{section_id}/pages"
        
        data = {
            "title": title,
            "content": content_html
        }
        try:
            response = requests.post(url, json=data, headers=get_headers(access_token))
            response.raise_for_status()
            page_id = response.json().get("id")
            log_operation(
                "info",
                f"Page created: {title} (ID: {page_id})",
                operation="create_page",
                object=title
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error creating page '{title}': {str(e)}",
                operation="create_page",
                object=title
            )
            return None

    def add_text_to_page(self, access_token: str, page_id: str, content_html: str) -> dict:
        """
        Add content to an existing OneNote page.
        """
        url = f"{self.notebook_base_url}pages/{page_id}/content"
        
        data = {
            "content": content_html
        }
        try:
            response = requests.patch(url, json=data, headers=get_headers(access_token))
            response.raise_for_status()
            log_operation(
                "info",
                f"Text added to page: {page_id}",
                operation="add_text_to_page",
                object=page_id
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error adding text to page '{page_id}': {str(e)}",
                operation="add_text_to_page",
                object=page_id
            )
            return None