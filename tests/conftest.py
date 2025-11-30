import pytest
import tempfile
import os
from cpcready.pydsk.dsk import DSK

@pytest.fixture
def temp_disk():
    with tempfile.TemporaryDirectory() as tmpdir:
        dsk_path = os.path.join(tmpdir, "test.dsk")
        dsk = DSK()
        dsk.create(40, 9)
        dsk.save(dsk_path)
        yield dsk_path

@pytest.fixture
def temp_bas():
    with tempfile.NamedTemporaryFile(suffix=".bas", delete=False) as f:
        f.write(b"10 PRINT \"HELLO WORLD\"\n20 GOTO 10\n")
        f.flush()
        yield f.name
    os.unlink(f.name)

@pytest.fixture(scope="session", autouse=True)
def cleanup_disks():
    yield
    import os
    for fname in [
        "disc_DATA.dsk", "disc_SYSTEM.dsk", "disc_VENDOR.dsk",
        "seq.dsk", "standalone.dsk", "test_disc.dsk", "test.dsk"
    ]:
        try:
            os.remove(fname)
        except FileNotFoundError:
            pass
