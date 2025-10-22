import pytest
from unittest.mock import patch
import API.Util.splitters as splitters
from langchain_core.documents import Document


def test_splitter_raises_for_unknown_type() -> None:
    """Ensure Splitter raises ValueError for unsupported splitter types."""
    docs = [Document(page_content="Sample text")]
    splitter = splitters.Splitter()
    with pytest.raises(ValueError, match="No splitter for 'UnknownType'"):
        splitter.split("UnknownType", docs)


def test_splitter_uses_recursive_character_splitter_from_default_registry() -> None:
    """Ensure the default RecursiveCharacterTextSplitterType instance’s split() method is called."""
    docs = [Document(page_content="Sample document text")]
    splitter = splitters.Splitter()

    with patch.object(splitter._registry["RecursiveCharacterTextSplitterType"], "split", return_value=["split_docs"]) as mock_split:
        result = splitter.split("RecursiveCharacterTextSplitterType", docs)
        assert result == ["split_docs"]
        mock_split.assert_called_once_with(docs)
