import pytest
from unittest.mock import patch
import API.Util.splitters as splitters
from langchain.schema import Document


def test_splitter_raises_for_unknown_type():
    """Ensure Splitter raises ValueError for unsupported splitter types."""
    docs = [Document(page_content="Sample text")]
    splitter = splitters.Splitter()
    with pytest.raises(ValueError, match="No splitter for 'UnknownType'"):
        splitter.split("UnknownType", docs)


def test_splitter_uses_recursive_splitter_from_default_registry():
    """Ensure the real registry entry for RecursiveSplitterType calls its split()."""
    docs = [Document(page_content="Sample document text")]

    # Patch the actual class in registry
    with patch.object(splitters.RecursiveSplitterType, "split", return_value=["split_docs"]) as mock_split:
        splitter = splitters.Splitter()  # uses default registry internally
        result = splitter.split("RecursiveSplitterType", docs)

        # Validate the call was made to the patched method
        assert result == ["split_docs"]
        mock_split.assert_called_once_with(docs)
