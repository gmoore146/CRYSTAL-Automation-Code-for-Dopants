import os
import shutil

# Base folder where elemental folders are located
base_folder = os.path.dirname(os.path.abspath(__file__))

# Detect elemental folders
element_folders = [f for f in os.listdir(base_folder)
                   if os.path.isdir(os.path.join(base_folder, f))]

if not element_folders:
    print("No elemental folders found. Exiting.")
    exit()

# Loop over each elemental folder
for element_folder in element_folders:
    folder_path = os.path.join(base_folder, element_folder)
    
    # Find all subfolders starting with '221_'
    subfolders_to_delete = [f for f in os.listdir(folder_path)
                            if os.path.isdir(os.path.join(folder_path, f)) and f.startswith("221_")]
    
    for subfolder in subfolders_to_delete:
        subfolder_path = os.path.join(folder_path, subfolder)
        try:
            shutil.rmtree(subfolder_path)
            print(f"Deleted {subfolder_path}")
        except Exception as e:
            print(f"Failed to delete {subfolder_path}: {e}")