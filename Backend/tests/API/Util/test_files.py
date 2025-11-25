import os
import uuid
import pytest
from unittest.mock import patch, MagicMock

from API.Util.files import (
    create_temp_file_from_bytes,
    convert_to_html,
    convert_to_html_bytes,
)


def test_create_temp_file_from_bytes_creates_and_deletes_temp_file():
    original_name = "test_document.pdf"
    data = b"hello world"

    with create_temp_file_from_bytes(original_name, data) as temp_path:
        # File should exist
        assert os.path.exists(temp_path)

        # Path should end with "_<original filename>"
        assert temp_path.endswith("_" + original_name)

        # UUID prefix check
        prefix = os.path.basename(temp_path).split("_")[0]
        uuid.UUID(prefix)  # will raise if invalid

        # File content should match
        with open(temp_path, "rb") as f:
            assert f.read() == data

    # After context manager, file should be deleted
    assert not os.path.exists(temp_path)


def test_convert_to_html_with_mocked_partition():
    # Mock element with working to_html()
    mock_element = MagicMock()
    mock_element.to_html.return_value = "<p>Hello</p>"

    with patch("API.Util.files.partition", return_value=[mock_element]) as mock_partition:
        html = convert_to_html(b"xxx", "file.docx")

    mock_partition.assert_called_once()
    assert html == "<p>Hello</p>"


def test_convert_to_html_falls_back_to_str_when_to_html_fails():
    bad_element = MagicMock()
    bad_element.to_html.side_effect = Exception("cannot convert")

    with patch("API.Util.files.partition", return_value=[bad_element]):
        html = convert_to_html(b"abc", "bad.docx")

    # Should fall back to str(element)
    assert html == str(bad_element)


def test_convert_to_html_bytes_encodes_utf8():
    with patch("API.Util.files.convert_to_html", return_value="<p>Text</p>") as mock_html:
        result = convert_to_html_bytes(b"xxx", "filename.docx")

    mock_html.assert_called_once()
    assert isinstance(result, bytes)
    assert result == b"<p>Text</p>"
