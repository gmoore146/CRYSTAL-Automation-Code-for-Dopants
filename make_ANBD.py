import os

base_folder = os.path.dirname(os.path.abspath(__file__))

templates_folder = os.path.join(base_folder, "templates")
anbd_template_file = os.path.join(templates_folder, "template_ANBD.txt")

if not os.path.exists(anbd_template_file):
    print(f"ANBD template file '{anbd_template_file}' not found. Exiting.")
    exit()

with open(anbd_template_file, "r") as f:
    anbd_template_lines = f.readlines()

element_folders = [f for f in os.listdir(base_folder)
                   if os.path.isdir(os.path.join(base_folder, f))]

if not element_folders:
    print("No elemental folders found. Exiting.")
    exit()

for element_folder in element_folders:
    folder_path = os.path.join(base_folder, element_folder)
    cel221_a25_path = os.path.join(folder_path, "cel221_A25")
    found_subfolder = False
    if os.path.isdir(cel221_a25_path) and not cel221_a25_path.endswith('.optstory'):
        anbd_output_file = os.path.join(cel221_a25_path, f"{element_folder}_ANBD.d3")
        if os.path.exists(anbd_output_file):
            print(f"Skipping {element_folder}: {anbd_output_file} already exists.")
        else:
            with open(anbd_output_file, "w") as f:
                f.writelines(anbd_template_lines)
            print(f"Generated {anbd_output_file}")
        found_subfolder = True

    if not found_subfolder:
        print(f"Skipping {element_folder}: no subfolder found.")