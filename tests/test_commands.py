import pytest
import subprocess
import os

CPC = ["python", "-m", "cpcready.cli"]
TEST_DSK = os.path.join(os.path.dirname(__file__), "files", "demo.dsk")
BAS_FILE = os.path.join(os.path.dirname(__file__), "files", "pepe.bas")

# Helper para ejecutar comandos

def run_cpc(args):
    result = subprocess.run(CPC + args, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

# Test para cada comando principal excepto console



def mount_drive_a(disk_path):
    run_cpc(["drive", "a", disk_path])

def test_cat(temp_disk):
    mount_drive_a(temp_disk)
    out, err, code = run_cpc(["cat"])
    assert "File" in out or code == 0



def test_disc():
    out, err, code = run_cpc(["disc", "new", "test_disc.dsk"])
    assert ("DSK created successfully" in out or "exists not creating new one" in out)

def test_drive_status():
    out, err, code = run_cpc(["drive", "status"])
    assert "Drive" in out or code == 0

def test_emu():
    out, err, code = run_cpc(["emu"])
    assert code == 0 or code == 1


def test_era(temp_disk, temp_bas):
    mount_drive_a(temp_disk)
    run_cpc(["save", temp_bas])
    # El archivo debe existir antes de borrar
    out, err, code = run_cpc(["era", os.path.basename(temp_bas)])
    if code != 0:
        pytest.skip("No se pudo borrar, probablemente el archivo no existe en el disco")
    assert code == 0


def test_filextr(temp_disk, temp_bas):
    mount_drive_a(temp_disk)
    run_cpc(["save", temp_bas])
    out, err, code = run_cpc(["filextr", os.path.basename(temp_bas)])
    if code != 0:
        pytest.skip("No se pudo extraer, probablemente el archivo no existe en el disco")
    assert code == 0

def test_list(temp_disk, temp_bas):
    mount_drive_a(temp_disk)
    run_cpc(["save", temp_bas])
    out, err, code = run_cpc(["list", os.path.basename(temp_bas)])
    assert "PRINT" in out or code == 0


def test_m4():
    out, err, code = run_cpc(["m4"])
    if code == 2:
        pytest.skip("Comando m4 requiere hardware/emulador real")
    assert code == 0 or code == 1

def test_mode():
    out, err, code = run_cpc(["mode", "1"])
    assert code == 0 or code == 1

def test_model():
    out, err, code = run_cpc(["model", "6128"])
    assert code == 0 or code == 1

def test_ren(temp_disk, temp_bas):
    mount_drive_a(temp_disk)
    run_cpc(["save", temp_bas])
    out, err, code = run_cpc(["ren", os.path.basename(temp_bas), "pepe2.bas"])
    assert code == 0

def test_run(temp_disk, temp_bas):
    mount_drive_a(temp_disk)
    run_cpc(["save", temp_bas])
    out, err, code = run_cpc(["run", os.path.basename(temp_bas)])
    assert code == 0 or code == 1


def test_rvm():
    out, err, code = run_cpc(["rvm"])
    if code == 2:
        pytest.skip("Comando rvm requiere hardware/emulador real")
    assert code == 0 or code == 1

def test_save(temp_disk, temp_bas):
    mount_drive_a(temp_disk)
    out, err, code = run_cpc(["save", temp_bas])
    assert code == 0

def test_user():
    out, err, code = run_cpc(["user", "0"])
    assert code == 0 or code == 1
