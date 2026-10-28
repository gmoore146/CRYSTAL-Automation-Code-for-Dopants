Python scripts for the making of .d12, .qsub, and .d3 file. These scripts leverage the CRYSTAL and PROPERTIES code, extracting info about periodic defective systems using quantum mechanics from first principle.

Scripts were run on HPC clusters, making used of parallelisation. 

.out files are automatically read by subsequent .d3 scripts.

PROPERTIES calculations include dos, ANBD, and band. 

See https://www.crystal.unito.it/index.html for more info regarding software.

## Layout

```
crystal_dopants/   the code (make_d12, make_d3, make_qsub, submit)
inputs/            dopant basis sets: line 1 element symbol, line 2 atomic number, then the basis block
templates/d12/     one CRYSTAL input template per defect site (file name = site label)
templates/d3/      PROPERTIES templates: dos.txt, band.txt, anbd.txt
runs/              generated: runs/<element>/<site>/... (git-ignored)
legacy/            older script versions, kept for reference
```

## Usage

Run from the project root. With [uv](https://docs.astral.sh/uv/):

```
uv run make-d12                    # runs/<el>/<site>/<el>_<site>.d12
uv run make-qsub scf               # .qsub for every .d12
uv run submit scf                  # pick an element folder, qsub its jobs
# after the SCF .out files exist:
uv run make-d3 dos                 # or band / ANBD
uv run make-qsub dos
uv run submit dos
```

Without uv (e.g. on the cluster), plain Python 3.8+ works: `python3 -m crystal_dopants.make_d12`,
`python3 -m crystal_dopants.make_d3 dos`, etc.

Tests: `uv run pytest`
