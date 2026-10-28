import os

base_folder = os.path.dirname(os.path.abspath(__file__))

qsub_template = """#!/bin/bash  --login
#PBS -N {element_band}
#PBS -l select=1:ncpus=96:mpiprocs=96:ompthreads=1:mem=128GB
#PBS -l walltime=1:00:00

echo "<qsub_standard_output>"
date
echo "<qstat -f $PBS_JOBID>"
qstat -f $PBS_JOBID
echo "</qstat -f $PBS_JOBID>"

export NCORES=96
export NPROCESSES=96
export PBS_O_WORKDIR=$(readlink -f $PBS_O_WORKDIR)
export OMP_NUM_THREADS=1
env
echo "</qsub_standard_output>"

cd $PBS_O_WORKDIR
touch wood
export MODULEPATH=$MODULEPATH:$HOME/../../gmallia/home/CRYSTAL17_cx1/v2gnu/modules
echo "MODULEPATH= "$MODULEPATH
echo Initial list of module loaded
module list -l
module load mpich/3.2.1
#/rds/general/user/gmallia/home/CRYSTAL17_cx1/v2gnu/runcryP {element_band} 
/rds/general/user/gmallia/home/CRYSTAL17_cx1/v2gnu/runpropP {element_band} {job_name_d12} 
                    
###
if [[ -f ./{element_band}.run ]];then
chmod 755 ./{element_band}.run
./{element_band}.run
fi
"""

element_folders = [f for f in os.listdir(base_folder)
                   if os.path.isdir(os.path.join(base_folder, f))]

if not element_folders:
    print("No elemental folders found. Exiting.")
    exit()

for element_folder in element_folders:
    element_folder_path = os.path.join(base_folder, element_folder)
    found_d3_files = []
    for root, dirs, files in os.walk(element_folder_path):
        for file in files:
            if file.endswith(".d3") and "band" in file:
                found_d3_files.append((root, file))
    
    if not found_d3_files:
        print(f"No .d3 files found in {element_folder_path}. Skipping.")
        continue
    
    for root, d3_file in found_d3_files:
        element_band = os.path.splitext(d3_file)[0]
        out_files = [f for f in os.listdir(root) if f.endswith(".out") and "band" not in f]
        if out_files:
            job_name_d12 = os.path.splitext(out_files[0])[0]
        else:
            job_name_d12 = element_band
        
        qsub_file_name = f"{element_band}.qsub"
        qsub_file_path = os.path.join(root, qsub_file_name)
        
        if os.path.exists(qsub_file_path):
            print(f"Skipped (already exists) -> {qsub_file_path}")
            continue

        qsub_content = qsub_template.format(
            element_band=element_band,
            job_name_d12=job_name_d12
        )

        with open(qsub_file_path, "w") as f:
            f.write(qsub_content)

        print(f"Generated {qsub_file_path}")