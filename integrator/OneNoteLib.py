import os

import requests

from integrator.integrator.logging_config import log_operation


class OneNoteLib:
    def __init__(self, base_url):
        """
        Initialize the OneNoteLib instance with a base URL.

        Args:
            base_url (str): The base URL for OneNote API. Defaults to Microsoft Graph API endpoint for OneNote.
        """
        self.base_url = base_url

    def get_notebook_url(self, notebook_id: str) -> str:
        """
        Generate the URL to access a specific notebook.
        """
        return f"{self.base_url}notebooks/{notebook_id}"

    def get_section_url(self, section_id: str) -> str:
        """
        Generate the URL to access a specific section.
        """
        return f"{self.base_url}sections/{section_id}"

    def get_page_url(self, page_id: str) -> str:
        """
        Generate the URL to access a specific page.
        """
        return f"{self.base_url}pages/{page_id}"

    def get_notebooks(self, access_token: str) -> dict:
        """
        Retrieve all notebooks for the authenticated user.
        """
        url = f"{self.base_url}notebooks"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            log_operation(
                "info",
                "Retrieved notebooks successfully",
                operation="get_notebooks",
                object="notebooks"
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            log_operation(
                "error",
                f"Error retrieving notebooks: {str(e)}",
                operation="get_notebooks",
                object="notebooks"
            )
            return None

    def get_notebook_structure(self, access_token: str, notebook_id: str) -> dict:
        """
        Get the structure of a notebook, including sections and pages.
        """
        url = f"{self.base_url}notebooks/{notebook_id}/sections"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            sections = response.json().get("value", [])
            notebook_structure = {}
            for section in sections:
                section_id = section['id']
                section_name = section['displayName']
                pages_url = f"{self.base_url}sections/{section_id}/pages"
                pages_response = requests.get(pages_url, headers=headers)
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
        url = f"{self.base_url}sections/{section_id}/pages"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "title": title,
            "content": content_html
        }
        try:
            response = requests.post(url, json=data, headers=headers)
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
        url = f"{self.base_url}pages/{page_id}/content"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "content": content_html
        }
        try:
            response = requests.patch(url, json=data, headers=headers)
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
