import os

base_folder = os.path.dirname(os.path.abspath(__file__))

d12_files = []
for root, dirs, files in os.walk(base_folder):
    for f in files:
        if f.endswith(".d12"):
            d12_files.append(os.path.join(root, f))

qsub_template = """#!/bin/bash  --login
#PBS -N {job_name}
#PBS -l select=1:ncpus=64:mpiprocs=64:ompthreads=1:mem=128GB
#PBS -l walltime=8:00:00

echo "<qsub_standard_output>"
date
echo "<qstat -f $PBS_JOBID>"
qstat -f $PBS_JOBID
echo "</qstat -f $PBS_JOBID>"

export NCORES=64
export NPROCESSES=64
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
/rds/general/user/gmallia/home/CRYSTAL17_cx1/v2gnu/runcryP {job_name} 
                     
###
if [[ -f ./{job_name}.run ]];then
chmod 755 ./{job_name}.run
./{job_name}.run
fi
"""

for d12_path in d12_files:
    job_name = os.path.splitext(os.path.basename(d12_path))[0]
    qsub_path = os.path.join(os.path.dirname(d12_path), f"{job_name}.qsub")
    if not os.path.exists(qsub_path):
        with open(qsub_path, "w") as f:
            f.write(qsub_template.format(job_name=job_name))
        print(f"Generated qsub script -> {qsub_path}")
    else:
        print(f"Skipped (already exists) -> {qsub_path}")