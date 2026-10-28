"""Submit .qsub jobs for one element folder with qsub, skipping queued/finished jobs.

Usage: submit {scf,dos,band,ANBD}
"""
import os
import re
import subprocess
import sys

from .common import KINDS, PROP_KINDS, RUNS, element_folders, is_prop_file


def wanted(kind, qsub_name):
    if kind == "scf":
        return not is_prop_file(qsub_name)
    return kind in qsub_name


def running_job_names(user):
    try:
        result = subprocess.run(["qstat", "-u", user], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, universal_newlines=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: Could not get running jobs. All jobs will be submitted.")
        return []
    # shortcut: assumes the job name is the 3rd column of `qstat -u`; on PBS Pro it is
    # usually the 4th (and truncated), so check this against your cluster's output
    return [line.split()[2] for line in result.stdout.splitlines()[2:] if len(line.split()) >= 3]


def job_name_of(qsub_path):
    with open(qsub_path) as f:
        for line in f:
            match = re.match(r"#PBS\s+-N\s+(\S+)", line)
            if match:
                return match.group(1)
    return os.path.splitext(os.path.basename(qsub_path))[0]


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in KINDS:
        sys.exit("Usage: submit {%s}" % ",".join(KINDS))
    kind = sys.argv[1]

    folders = element_folders()
    if not folders:
        sys.exit("No elemental folders found in runs/.")

    print("Detected elemental folders:")
    for i, folder in enumerate(folders, start=1):
        print(f"{i}: {folder}")
    selection = input("Enter the number of the folder you want to submit: ").strip()
    try:
        index = int(selection) - 1
        if index < 0 or index >= len(folders):
            raise ValueError
    except ValueError:
        sys.exit("Invalid selection. Exiting.")

    selected = folders[index]
    folder_path = os.path.join(RUNS, selected)
    print(f"Checking jobs in folder '{selected}' ...")

    user = os.environ.get("USER") or input("Enter your HPC username: ").strip()
    running = running_job_names(user)

    qsub_files = [os.path.join(root, f)
                  for root, dirs, files in os.walk(folder_path)
                  for f in sorted(files) if f.endswith(".qsub") and wanted(kind, f)]
    if not qsub_files:
        sys.exit(f"No {kind} .qsub files found in any subfolder of '{selected}'.")

    for qsub_path in qsub_files:
        qsub_folder = os.path.dirname(qsub_path)

        if kind in PROP_KINDS:
            existing = [f for f in os.listdir(qsub_folder) if f.endswith(".out") and kind in f]
            if existing:
                print(f"Skipping {qsub_path}: {kind} .out file(s) already exist -> {existing}")
                continue

        job_name = job_name_of(qsub_path)
        if job_name in running:
            print(f"Skipping {qsub_path}: job '{job_name}' is already running or queued.")
            continue

        print(f"Submitting {qsub_path} from folder '{qsub_folder}' ...")
        try:
            result = subprocess.run(["qsub", qsub_path], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True,
                                    check=True, cwd=qsub_folder)
            print(f"Submitted {qsub_path}, output:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error submitting {qsub_path}:\n{e.stderr}")


if __name__ == "__main__":
    main()
