import os

# Base folders
base_folder = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(base_folder, "inputs")
templates_folder = os.path.join(base_folder, "templates")

# Spinlock mapping
spinlock_map = {
    '3': '2', '4': '1', '6': '1', '12': '1', '14': '1', '20': '1', '21': '2', '22': '1',
    '23': '2', '24': '3', '25': '4', '26': '3', '27': '2', '28': '1', '29': '2', '30': '1',
    '32': '1', '48': '1', '46': '1', '47': '2', '50': '1', '38': '1', '78': '1', '282': '1'
}

# Detect templates
template_files = {}        # normal templates
template_nohess_files = {} # templates with nohess
for file in os.listdir(templates_folder):
    filename_lower = file.lower()
    if file.startswith("template_") and file.endswith(".txt") \
       and "prop" not in filename_lower and "band" not in filename_lower:
        site_label = file.replace("template_", "").replace(".txt", "")
        if "nohess" in filename_lower:
            template_nohess_files[site_label] = os.path.join(templates_folder, file)
        else:
            template_files[site_label] = os.path.join(templates_folder, file)

print("Detected normal templates:", list(template_files.keys()))
print("Detected nohess templates:", list(template_nohess_files.keys()))

# Detect dopants
dopant_files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]

def modify_input(template_lines, basis_file_path):
    """Replace placeholders in template with dopant info."""
    new_lines = []
    with open(basis_file_path, "r") as bf:
        bf_lines = bf.readlines()

    element_symbol = bf_lines[0].strip()
    dopant_z = bf_lines[1].strip()
    basis_lines = bf_lines[2:]

    spinlock_value = spinlock_map.get(dopant_z, '0')

    for line in template_lines:
        if "<DOPANT_ATOMIC_NUMBER>" in line:
            new_lines.append(line.replace("<DOPANT_ATOMIC_NUMBER>", dopant_z))
        elif "<BASIS_SET_BLOCK>" in line:
            new_lines.extend(basis_lines)
        elif "<SPIN_LOCK>" in line:
            new_lines.append(line.replace("<SPIN_LOCK>", spinlock_value))
        else:
            new_lines.append(line)

    return new_lines, dopant_z, element_symbol

# Main loop
for dopant_file in dopant_files:
    basis_path = os.path.join(input_folder, dopant_file)
    with open(basis_path, "r") as bf:
        element_symbol = bf.readline().strip()

    element_folder = os.path.join(base_folder, element_symbol)
    os.makedirs(element_folder, exist_ok=True)

    for site_label in template_files.keys():
        # Prepare site folder
        site_folder = os.path.join(element_folder, site_label)
        os.makedirs(site_folder, exist_ok=True)

        # Determine if normal or nohess template and file name
        normal_output_file = os.path.join(site_folder, f"{element_symbol}_{site_label}.d12")
        nohess_output_file = os.path.join(site_folder, f"{element_symbol}_{site_label}_nohess.d12")

        if not os.path.exists(normal_output_file) and site_label in template_nohess_files:
            template_file = template_nohess_files[site_label]
            output_file = nohess_output_file
        else:
            # If normal file exists, skip it
            if os.path.exists(normal_output_file):
                print(f"Skipped (already exists) -> {normal_output_file}")
                continue
            template_file = template_files[site_label]
            output_file = normal_output_file

        # Read template and generate input
        with open(template_file, "r") as f:
            template_lines = f.readlines()

        new_input, dopant_z, _ = modify_input(template_lines, basis_path)

        # Write file only if it does not exist
        if not os.path.exists(output_file):
            with open(output_file, "w") as f:
                f.writelines(new_input)
            print(f"Generated input -> {output_file}")