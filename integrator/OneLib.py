import re
from urllib.parse import parse_qs, urlparse


def extract_folder_id(url: str) -> str:
    # Parse the URL and extract the query parameters
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Extract the 'id' parameter
    folder_id = query_params.get("id", [None])[0]
    
    if folder_id:
        return folder_id
    else:
        raise ValueError("Folder ID not found in the URL")

def list_all_attributes(obj) -> str:
    """Print all attributes of an object."""
    txt = ""
    for key, value in obj.items():
        txt += f"  {key}: {value}\n"
    return txt

def get_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}

def is_notebook(obj):
    """Identify OneDrive objects."""
    # Check if 'package' exists and its 'type' is 'oneNote'
    package = obj.get('package')
    if package and package.get('type') == 'oneNote':
        return True
    return False

def get_id_from_dict(items: list[dict], item_name: str, key: str = "name") -> str | None:
    """
    Get the ID of an item (notebook, section, or page) from a list of dictionaries.

    Args:
        items (list[dict]): The list of items to search.
        item_name (str): The name of the item to find.
        key (str): The key to match the name against (default is "name").

    Returns:
        str | None: The ID of the matched item, or None if no match is found.
    """
    for item in items:
        if item.get(key) == item_name:
            return item.get("id")
    return None
