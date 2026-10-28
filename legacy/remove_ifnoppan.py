import os
import shutil

# Base folder containing elemental folders
base_folder = "/rds/general/user/gef22/home/Ga2O3/HSE06/defects/auto"

# Loop over elemental folders
for element in os.listdir(base_folder):
    element_path = os.path.join(base_folder, element)
    if not os.path.isdir(element_path):
        continue

    # Loop over subfolders starting with '221'
    for subfolder in os.listdir(element_path):
        if subfolder.startswith("221"):
            subfolder_path = os.path.join(element_path, subfolder)
            if not os.path.isdir(subfolder_path):
                continue

            # Check for .PPAN files
            ppan_files = [f for f in os.listdir(subfolder_path) if f.endswith(".PPAN")]
            if ppan_files:
                print(f"{subfolder_path} -> Found .PPAN file(s): {', '.join(ppan_files)}")
            else:
                print(f"{subfolder_path} -> No .PPAN files found, removing all contents")
                # Remove all contents of the folder
                for item in os.listdir(subfolder_path):
                    item_path = os.path.join(subfolder_path, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)