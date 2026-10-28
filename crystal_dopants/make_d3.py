"""Make PROPERTIES .d3 inputs next to each finished SCF .out.

Usage: make-d3 {dos,band,ANBD}
"""
import math
import os
import sys

from .common import PROP_KINDS, TEMPLATES, element_folders, parse_electrons, scf_out_files


def band_range(total_electrons, core_electrons):
    return math.floor(core_electrons / 2 + 1), math.ceil(total_electrons / 2 + 5)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in PROP_KINDS:
        sys.exit("Usage: make-d3 {%s}" % ",".join(PROP_KINDS))
    kind = sys.argv[1]

    template_file = os.path.join(TEMPLATES, "d3", kind.lower() + ".txt")
    with open(template_file) as f:
        template = f.read()

    folders = element_folders()
    if not folders:
        sys.exit("No elemental folders found in runs/. Exiting.")

    for element in folders:
        found = False
        for root, out_file in scf_out_files(element):
            found = True
            out_path = os.path.join(root, out_file)
            output_file = os.path.join(root, f"{element}_{kind}.d3")
            if os.path.exists(output_file):
                print(f"Skipping {element}: {output_file} already exists.")
                continue

            electrons = parse_electrons(out_path)
            if electrons is None:
                print(f"Skipping {element}: could not parse electrons from {out_path}")
                continue
            valence, conduction = band_range(*electrons)

            content = (template.replace("<ELEMENT>", element)
                       .replace("<VALENCE_BAND>", str(valence))
                       .replace("<CONDUCTION_BAND>", str(conduction)))
            with open(output_file, "w") as f:
                f.write(content)
            print(f"Generated {output_file} with VALENCE_BAND={valence}, CONDUCTION_BAND={conduction}")

        if not found:
            print(f"Skipping {element}: no SCF .out file found in any subfolder.")


if __name__ == "__main__":
    main()
