import os

base_folder = os.path.dirname(os.path.abspath(__file__))

d12_files = [f for f in os.listdir(base_folder) if f.endswith(".d12")]

qsub_template = """#!/bin/bash  --login
#PBS -N {job_name}
#PBS -l select=1:ncpus=64:mpiprocs=64:ompthreads=1:mem=128GB
#PBS -l walltime=8:00:00

echo "<qsub_standard_output>"
date
echo "<qstat -f $PBS_JOBID>"
qstat -f $PBS_JOBID
echo "</qstat -f $PBS_JOBID>"

# number of cores per node used
export NCORES=64
# number of processes
export NPROCESSES=64

# Make sure any symbolic links are resolved to absolute path
export PBS_O_WORKDIR=$(readlink -f $PBS_O_WORKDIR)

# Set the number of threads to 1
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

for d12_file in d12_files:
    job_name = os.path.splitext(d12_file)[0] 
    output_file = os.path.join(base_folder, f"{job_name}.qsub")
    with open(output_file, "w") as f:
        f.write(qsub_template.format(job_name=job_name))
    print(f"Generated qsub script -> {output_file}")