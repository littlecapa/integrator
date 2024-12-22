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


