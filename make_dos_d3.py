import os
import math  

base_folder = os.path.dirname(os.path.abspath(__file__))

templates_folder = os.path.join(base_folder, "templates")
template_file = os.path.join(templates_folder, "template_dos.txt")

if "dos" not in os.path.basename(template_file) or not template_file.endswith(".txt"):
    print(f"Template file '{template_file}' does not contain 'dos' in its name or does not end with .txt. Exiting.")
    exit()

if not os.path.exists(template_file):
    print(f"Template file '{template_file}' not found. Exiting.")
    exit()

with open(template_file, "r") as f:
    template_lines = f.readlines()

exclude_folders = {"templates", "inputs"}
element_folders = [f for f in os.listdir(base_folder)
                   if os.path.isdir(os.path.join(base_folder, f)) and f not in exclude_folders]

if not element_folders:
    print("No elemental folders found. Exiting.")
    exit()

for element_folder in element_folders:
    folder_path = os.path.join(base_folder, element_folder)
    target_out_file = f"{element_folder}_cel221_A25.out"
    out_file_path = None

    for root, dirs, files in os.walk(folder_path):
        if target_out_file in files:
            out_file_path = os.path.join(root, target_out_file)
            break

    if not out_file_path:
        print(f"Skipping {element_folder}: {target_out_file} not found in any subfolder.")
        continue

    total_electrons = None
    core_electrons = None
    with open(out_file_path, "r") as f:
        for line in f:
            if "N. OF ELECTRONS PER CELL" in line:
                parts = line.split()
                total_electrons = int(parts[5])
            elif "CORE ELECTRONS PER CELL" in line:
                parts = line.split()
                core_electrons = int(parts[4])
            if total_electrons is not None and core_electrons is not None:
                break

    if total_electrons is None or core_electrons is None:
        print(f"Skipping {element_folder}: could not parse electrons from {out_file_path}")
        continue

    valence_band = math.floor(core_electrons / 2 + 1)
    conduction_band = math.ceil(total_electrons / 2 + 5)

    output_file = os.path.join(root, f"{element_folder}_dos.d3")

    if os.path.exists(output_file):
        print(f"Skipping {element_folder}: {output_file} already exists.")
        continue

    new_lines = []
    for line in template_lines:
        line = line.replace("<ELEMENT>", element_folder)
        line = line.replace("<VALENCE_BAND>", str(valence_band))
        line = line.replace("<CONDUCTION_BAND>", str(conduction_band))
        new_lines.append(line)

    with open(output_file, "w") as f:
        f.writelines(new_lines)

    print(f"Generated {output_file} with VALENCE_BAND={valence_band}, CONDUCTION_BAND={conduction_band}")