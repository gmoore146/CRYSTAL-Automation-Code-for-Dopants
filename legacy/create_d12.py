import os

base_folder = os.path.dirname(os.path.abspath(__file__))

input_folder = os.path.join(base_folder, "inputs")

template_file = os.path.join(base_folder, "template.txt")

site_label = "oct"

dopants = [
    {"basis_file": "si_basis.txt"},
    #add more as needed
]

with open(template_file, "r") as f:
    template_lines = f.readlines()

def modify_input(template_lines, dopant):
    """Use second line as atomic number for template and third+ lines for basis"""
    new_lines = []
    basis_path = os.path.join(input_folder, dopant["basis_file"])
    with open(basis_path, "r") as bf:
        bf_lines = bf.readlines()
    element_symbol = bf_lines[0].strip()  #first line = element symbol
    dopant_z = bf_lines[1].strip()        #second line = atomic number
    basis_lines = bf_lines[2:]            #third line onward = basis set

    for line in template_lines:
        if "<DOPANT_ATOMIC_NUMBER>" in line:
            new_lines.append(line.replace("<DOPANT_ATOMIC_NUMBER>", dopant_z))
        elif "<BASIS_SET_BLOCK>" in line:
            new_lines.extend(basis_lines)
        else:
            new_lines.append(line)
    return new_lines, dopant_z, element_symbol

for dopant in dopants:
    new_input, dopant_z, element_symbol = modify_input(template_lines, dopant)
    output_file = os.path.join(base_folder, f"{element_symbol}_{site_label}.d12")
    with open(output_file, "w") as f:
        f.writelines(new_input)
    print(f"Generated input -> {output_file}")