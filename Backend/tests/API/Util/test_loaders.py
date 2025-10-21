import pytest
from unittest.mock import patch
import API.Util.loaders as loaders


def test_loader_raises_for_unknown_type():
    """Ensure Loader raises ValueError for unsupported file types."""
    sample_xyz_bytes = b"%XYZ- 1.4 fake pdf data"
    loader = loaders.Loader()
    with pytest.raises(ValueError, match="No loader for 'xyz'"):
        loader.load("unknown.xyz", "xyz", sample_xyz_bytes)


def test_loader_uses_pdf_loader_from_default_registry() -> None:
    """Ensure the default PDF loader instance’s .load() method is called."""
    sample_pdf_bytes = b"%PDF-1.4 fake pdf data"
    loader = loaders.Loader()

    with patch.object(loader._registry["pdf"], "load", return_value=["pdf_doc"]) as mock_load:
        result = loader.load("lecture1.pdf", "pdf", sample_pdf_bytes)
        assert result == ["pdf_doc"]
        mock_load.assert_called_once_with("lecture1.pdf", sample_pdf_bytes)


def test_loader_uses_docx_loader_from_default_registry() -> None:
    """Ensure the default DOCX loader instance’s .load() method is called."""
    sample_docx_bytes = b"PK\x03\x04 fake docx data"
    loader = loaders.Loader()

    with patch.object(loader._registry["docx"], "load", return_value=["docx_doc"]) as mock_load:
        result = loader.load("report.docx", "docx", sample_docx_bytes)
        assert result == ["docx_doc"]
        mock_load.assert_called_once_with("report.docx", sample_docx_bytes)
