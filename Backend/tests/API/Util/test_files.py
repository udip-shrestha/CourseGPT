import os
import pytest
from API.Util.files import create_temp_file_from_bytes  # adjust path as needed


def test_create_temp_file_from_bytes_creates_file_and_writes_data():
    """Should create a real temp file and write bytes correctly."""
    data = b"Hello, World!"
    suffix = ".txt"

    with create_temp_file_from_bytes(suffix, data) as file_path:
        # File should exist
        assert os.path.exists(file_path)
        assert file_path.endswith(suffix)

        # Read back contents
        with open(file_path, "rb") as f:
            contents = f.read()
        assert contents == data

    # After context, file should still exist (delete=False)
    assert os.path.exists(file_path)

    # Manual cleanup
    os.remove(file_path)
    assert not os.path.exists(file_path)


def test_create_temp_file_from_bytes_with_empty_data():
    """Should handle empty bytes gracefully."""
    data = b""
    with create_temp_file_from_bytes(".bin", data) as file_path:
        assert os.path.exists(file_path)
        assert os.path.getsize(file_path) == 0
    os.remove(file_path)


def test_create_temp_file_from_bytes_returns_unique_files():
    """Each invocation should produce a different file path."""
    with create_temp_file_from_bytes(".tmp", b"data1") as path1, \
         create_temp_file_from_bytes(".tmp", b"data2") as path2:
        assert path1 != path2
        assert os.path.exists(path1)
        assert os.path.exists(path2)

    # Cleanup both
    os.remove(path1)
    os.remove(path2)
