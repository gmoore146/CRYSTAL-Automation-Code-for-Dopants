from crystal_dopants.make_d3 import band_range
from crystal_dopants.make_qsub import qsub_content
from crystal_dopants.submit import wanted


def test_band_range():
    assert band_range(total_electrons=100, core_electrons=40) == (21, 55)


def test_qsub_content():
    scf = qsub_content("scf", "Ca_cel221_A25")
    assert "runcryP Ca_cel221_A25" in scf and "walltime=8:00:00" in scf
    dos = qsub_content("dos", "Ca_dos", "Ca_cel221_A25")
    assert "runpropP Ca_dos Ca_cel221_A25" in dos and "ncpus=128" in dos


def test_wanted():
    assert wanted("scf", "Ca_cel221_A25.qsub") and not wanted("scf", "Ca_dos.qsub")
    assert wanted("band", "Ca_band.qsub") and not wanted("band", "Ca_dos.qsub")
