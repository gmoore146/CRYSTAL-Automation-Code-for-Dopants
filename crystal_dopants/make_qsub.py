"""Make PBS .qsub job scripts.

Usage: make-qsub {scf,dos,band,ANBD}
  scf:        one job per .d12 (runcryP)
  dos/band/ANBD: one job per matching .d3 (runpropP, reads the SCF run in the same folder)
"""
import os
import sys

from .common import KINDS, RUNS, is_prop_file

CRYSTAL = "/rds/general/user/gmallia/home/CRYSTAL17_cx1/v2gnu"

# (ncpus, mem, walltime) per calculation kind
RESOURCES = {
    "scf": (128, "920GB", "8:00:00"),
    "dos": (128, "920GB", "3:00:00"),
    "band": (96, "128GB", "1:00:00"),
    "ANBD": (96, "128GB", "1:00:00"),
}

QSUB_TEMPLATE = """#!/bin/bash  --login
#PBS -N {job_name}
#PBS -l select=1:ncpus={ncpus}:mpiprocs={ncpus}:ompthreads=1:mem={mem}
#PBS -l walltime={walltime}

echo "<qsub_standard_output>"
date
echo "<qstat -f $PBS_JOBID>"
qstat -f $PBS_JOBID
echo "</qstat -f $PBS_JOBID>"

export NCORES={ncpus}
export NPROCESSES={ncpus}
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
{run_command}
###
if [[ -f ./{job_name}.run ]];then
chmod 755 ./{job_name}.run
./{job_name}.run
fi
"""


def qsub_content(kind, job_name, scf_name=None):
    ncpus, mem, walltime = RESOURCES[kind]
    if kind == "scf":
        run_command = f"{CRYSTAL}/runcryP {job_name} "
    else:
        run_command = f"{CRYSTAL}/runpropP {job_name} {scf_name} "
    return QSUB_TEMPLATE.format(job_name=job_name, ncpus=ncpus, mem=mem,
                                walltime=walltime, run_command=run_command)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in KINDS:
        sys.exit("Usage: make-qsub {%s}" % ",".join(KINDS))
    kind = sys.argv[1]

    for root, dirs, files in os.walk(RUNS):
        for f in sorted(files):
            if kind == "scf":
                if not f.endswith(".d12"):
                    continue
            elif not (f.endswith(".d3") and kind in f):
                continue

            job_name = os.path.splitext(f)[0]
            scf_name = None
            if kind != "scf":
                outs = sorted(o for o in files if o.endswith(".out") and not is_prop_file(o))
                scf_name = os.path.splitext(outs[0])[0] if outs else job_name

            qsub_path = os.path.join(root, f"{job_name}.qsub")
            if os.path.exists(qsub_path):
                print(f"Skipped (already exists) -> {qsub_path}")
                continue
            with open(qsub_path, "w") as fh:
                fh.write(qsub_content(kind, job_name, scf_name))
            print(f"Generated {qsub_path}")


if __name__ == "__main__":
    main()
