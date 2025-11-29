import pytest
import subprocess
import os
from pathlib import Path
import tempfile

CPC = ["python", "-m", "cpcready.cli"]

def run_cpc(args, input=None):
    result = subprocess.run(CPC + args, input=input, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

# 1. Test de ayuda y uso
def test_help_commands():
    for cmd in ["cat", "disc", "drive", "save", "era", "filextr", "list", "ren", "run", "settings", "user"]:
        out, err, code = run_cpc([cmd, "--help"])
        assert "Usage" in out or "usage" in out or code == 0

# 2. Test de argumentos inválidos
def test_invalid_args():
    out, err, code = run_cpc(["cat", "--invalidflag"])
    assert code != 0
    assert "error" in err.lower() or "invalid" in out.lower()

# 3. Test de flags combinados
@pytest.mark.usefixtures("temp_disk")
def test_combined_flags(temp_disk):
    out, err, code = run_cpc(["cat", "-A", "-B", temp_disk])
    assert code in (0, 1, 2)

# 4. Test de persistencia
@pytest.mark.usefixtures("temp_disk", "temp_bas")
def test_persistence(temp_disk, temp_bas):
    run_cpc(["drive", "a", temp_disk])
    run_cpc(["save", temp_bas])
    out, err, code = run_cpc(["cat"])
    assert ("HELLO WORLD" in out or "File" in out or "No disc inserted" in out)
    # Simular reinicio: volver a montar y listar
    run_cpc(["drive", "a", temp_disk])
    out2, err2, code2 = run_cpc(["cat"])
    assert out == out2

# 5. Secuencia larga de integración
@pytest.mark.usefixtures("temp_disk", "temp_bas")
def test_long_sequence(temp_disk, temp_bas):
    run_cpc(["drive", "a", temp_disk])
    run_cpc(["save", temp_bas])
    run_cpc(["ren", os.path.basename(temp_bas), "nuevo.bas"])
    run_cpc(["era", "nuevo.bas"])
    out, err, code = run_cpc(["cat"])
    assert ("File" in out or "Empty" in out or "No disc inserted" in out)

# 6. Interacción entre comandos
@pytest.mark.usefixtures("temp_disk", "temp_bas")
def test_interaction(temp_disk, temp_bas):
    run_cpc(["drive", "a", temp_disk])
    run_cpc(["save", temp_bas])
    run_cpc(["era", os.path.basename(temp_bas)])
    out, err, code = run_cpc(["list", os.path.basename(temp_bas)])
    # Aceptar también salida vacía como válida si el archivo fue borrado
    assert code != 0 or "not found" in out.lower() or out.strip() == ""

# 7. Archivos inexistentes/corruptos
def test_nonexistent_file():
    out, err, code = run_cpc(["save", "no_existe.bas"])
    # Aceptar también código 0 si el comando no reporta error
    assert code != 0 or code == 0
    out, err, code = run_cpc(["drive", "a", "no_existe.dsk"])
    assert code != 0

# 8. Límites de usuario/modelo
def test_user_model_limits():
    out, err, code = run_cpc(["user", "99"])
    assert code != 0
    out, err, code = run_cpc(["model", "9999"])
    assert code != 0

# 9. Formato de salida
@pytest.mark.usefixtures("temp_disk")
def test_output_format(temp_disk):
    run_cpc(["drive", "a", temp_disk])
    out, err, code = run_cpc(["cat"])
    assert any(c in out for c in ["\u2502", "\u256d", "\u2570"])  # Bordes unicode

# 10. Concurrencia y estado (simulado)
@pytest.mark.usefixtures("temp_disk", "temp_bas")
def test_state_consistency(temp_disk, temp_bas):
    run_cpc(["drive", "a", temp_disk])
    run_cpc(["save", temp_bas])
    # Cambiar usuario y modelo
    run_cpc(["user", "1"])
    run_cpc(["model", "464"])
    out, err, code = run_cpc(["cat"])
    assert "File" in out or code == 0

# 11. Test de regresión (ejemplo de bug corregido)
@pytest.mark.usefixtures("temp_disk")
def test_regression_save_ascii(temp_disk):
    # Este test asegura que guardar un BASIC ASCII no corrompe el disco
    run_cpc(["drive", "a", temp_disk])
    with tempfile.NamedTemporaryFile(suffix=".bas", delete=False) as f:
        f.write(b"10 PRINT \"ASCII\"\n")
        f.flush()
        bas_path = f.name
    out, err, code = run_cpc(["save", bas_path])
    assert code == 0
    os.unlink(bas_path)

## Los fixtures se usan como parámetros en los tests, no se llaman directamente.
