import os
import subprocess
import re

base_folder = os.path.dirname(os.path.abspath(__file__))

element_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

if not element_folders:
    print("No elemental folders found.")
    exit()

print("Detected elemental folders:")
for i, folder in enumerate(element_folders, start=1):
    print(f"{i}: {folder}")

selection = input("Enter the number of the folder you want to submit: ").strip()
try:
    index = int(selection) - 1
    if index < 0 or index >= len(element_folders):
        raise ValueError
except ValueError:
    print("Invalid selection. Exiting.")
    exit()

selected_folder = element_folders[index]
folder_path = os.path.join(base_folder, selected_folder)
print(f"Checking jobs in folder '{selected_folder}' ...")

try:
    user = os.environ['USER']
except KeyError:
    user = input("Enter your HPC username: ").strip()

running_jobs = []
try:
    result = subprocess.run(
        ["qstat", "-u", user],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=True
    )
    lines = result.stdout.splitlines()[2:]
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            running_jobs.append(parts[2])
except subprocess.CalledProcessError:
    print("Warning: Could not get running jobs. All jobs will be submitted.")

qsub_files = []
for root, dirs, files in os.walk(folder_path):
    for f in files:
        if f.endswith(".qsub"):
            qsub_files.append(os.path.join(root, f))

if not qsub_files:
    print(f"No .qsub files found in folder '{selected_folder}'.")
    exit()

for qsub_path in qsub_files:
    job_name = None
    with open(qsub_path, "r") as f:
        for line in f:
            match = re.match(r"#PBS\s+-N\s+(\S+)", line)
            if match:
                job_name = match.group(1)
                break
    if not job_name:
        job_name = os.path.splitext(os.path.basename(qsub_path))[0]

    if job_name in running_jobs:
        print(f"Skipping {qsub_path}: job '{job_name}' is already running or queued.")
        continue

    qsub_folder = os.path.dirname(qsub_path)
    print(f"Submitting {qsub_path} from folder '{qsub_folder}' ...")
    try:
        result = subprocess.run(
            ["qsub", qsub_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True,
            cwd=qsub_folder
        )
        print(f"Submitted {qsub_path}, output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error submitting {qsub_path}:\n{e.stderr}")