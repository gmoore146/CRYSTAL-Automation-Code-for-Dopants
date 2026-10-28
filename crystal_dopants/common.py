import os

# Run commands from the project root: inputs/ and templates/ are read from there,
# generated element folders go in runs/.
ROOT = os.getcwd()
INPUTS = os.path.join(ROOT, "inputs")
TEMPLATES = os.path.join(ROOT, "templates")
RUNS = os.path.join(ROOT, "runs")

# PROPERTIES calculation kinds; "scf" is the main CRYSTAL run on the .d12
PROP_KINDS = ("dos", "band", "ANBD")
KINDS = ("scf",) + PROP_KINDS


def element_folders():
    if not os.path.isdir(RUNS):
        return []
    return sorted(f for f in os.listdir(RUNS) if os.path.isdir(os.path.join(RUNS, f)))


def is_prop_file(name):
    return any(k in name for k in PROP_KINDS)


def scf_out_files(element_folder):
    """Yield (dir, out_file) for every SCF .out under an element folder."""
    for root, dirs, files in os.walk(os.path.join(RUNS, element_folder)):
        for f in sorted(files):
            if f.endswith(".out") and not is_prop_file(f):
                yield root, f


def parse_electrons(out_path):
    """Return (total, core) electrons per cell from a CRYSTAL .out, or None."""
    total = core = None
    with open(out_path) as f:
        for line in f:
            if "N. OF ELECTRONS PER CELL" in line:
                total = int(line.split()[5])
            elif "CORE ELECTRONS PER CELL" in line:
                core = int(line.split()[4])
            if total is not None and core is not None:
                return total, core
    return None
