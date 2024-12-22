import json
import os

from integrator.integrator.OneDriveLib import OneDriveLib
from integrator.integrator.OneDriveTokenManager import OneDriveTokenManager
from integrator.integrator.testlib import (get_default_config_path,
                                           get_default_testfile_folder)


def dump_folder_structure_to_json(output_filename = "folder_structure.json"):
    """
    Test function to fetch and dump OneDrive folder structure into a JSON file.
    """
    token_manager = OneDriveTokenManager(get_default_config_path())
    access_token = token_manager.get_access_token()
    base_folder_url = token_manager.get_base_folder_url()
    print(f"Base Folder URL: {base_folder_url}")

    if not access_token:
        print("Failed to acquire access token.")
        return

    one_drive = OneDriveLib()
    folder_structure = one_drive.get_folders(access_token)
    #folder_structure = one_drive.get_folders(access_token, base_folder_url)

    output_file = os.path.join(get_default_testfile_folder(), output_filename)
    # Write the folder structure to a JSON file
    with open(output_file, "w") as file:
        print(folder_structure)
        json.dump(folder_structure, file, indent=4)

    print(f"Folder structure dumped to {output_file}")

if __name__ == "__main__":
    dump_folder_structure_to_json()