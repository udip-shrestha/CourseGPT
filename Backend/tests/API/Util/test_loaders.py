import pytest
from unittest.mock import patch

import API.Util.loaders as loaders


def test_loader_raises_for_unknown_type():
    """Ensure Loader raises ValueError for unsupported file types."""
    sample_xyz_bytes = b"%XYZ- 1.4 fake pdf data"
    loader = loaders.Loader()
    with pytest.raises(ValueError, match="No loader for 'xyz'"):
        loader.load("xyz", sample_xyz_bytes)


def test_loader_uses_pdf_loader_from_default_registry():
    """Ensure the real registry entry for PDF calls PDFLoaderType.load()."""
    sample_pdf_bytes = b"%PDF-1.4 fake pdf data"

    # Patch the *object already in the registry*
    with patch.object(loaders.PDFLoaderType, "load", return_value=["pdf_doc"]) as mock_load:
        loader = loaders.Loader()  # uses default registry internally
        result = loader.load("pdf", sample_pdf_bytes)

        # Now we’re testing real default behavior:
        assert result == ["pdf_doc"]
        mock_load.assert_called_once_with(sample_pdf_bytes)


def test_loader_uses_docx_loader_from_default_registry():
    """Ensure the real registry entry for DOCX calls DocxLoaderType.load()."""
    sample_docx_bytes = b"PK\x03\x04 fake docx data"

    with patch.object(loaders.DocxLoaderType, "load", return_value=["docx_doc"]) as mock_load:
        loader = loaders.Loader()
        result = loader.load("docx", sample_docx_bytes)

        assert result == ["docx_doc"]
        mock_load.assert_called_once_with(sample_docx_bytes)
