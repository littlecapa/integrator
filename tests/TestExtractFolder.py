import unittest
from urllib.parse import parse_qs, urlparse


# Function to extract the folder ID from the OneDrive URL
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

# Unit test class
class TestExtractFolderId(unittest.TestCase):
    
    def test_extract_folder_id_valid(self):
        # Test case with a valid OneDrive URL
        url = "https://onedrive.live.com/?id=66899B659FC7C342%21171081&cid=66899B659FC7C342"
        expected_folder_id = "66899B659FC7C342!171081"
        
        folder_id = extract_folder_id(url)
        self.assertEqual(folder_id, expected_folder_id)
    
    def test_extract_folder_id_invalid(self):
        # Test case with an invalid URL (no 'id' parameter)
        url = "https://onedrive.live.com/?cid=66899B659FC7C342"
        
        with self.assertRaises(ValueError):
            extract_folder_id(url)

    def test_extract_folder_id_missing_id(self):
        # Test case with an empty URL or missing 'id' parameter
        url = "https://onedrive.live.com/"
        
        with self.assertRaises(ValueError):
            extract_folder_id(url)

if __name__ == "__main__":
    unittest.main()
