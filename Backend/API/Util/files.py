import tempfile
from contextlib import contextmanager

@contextmanager
def create_temp_file_from_bytes(suffix: str, data: bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        tmp.flush()
        yield tmp.name
