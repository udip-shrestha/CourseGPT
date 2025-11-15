from typing import Protocol, List, Dict, Type, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ISplitterType(Protocol):
    """Splits documents into smaller text chunks."""
    def split(self, docs: List[Document]) -> List[Document]:
        ...


class RecursiveCharacterTextSplitterType(ISplitterType):
    """Splits documents using RecursiveCharacterTextSplitter."""
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def split(self, docs: List[Document]) -> List[Document]:
        return self.splitter.split_documents(docs)


class Splitter:
    """Factory that delegates document splitting by type."""
    _DEFAULT_REGISTRY: Dict[str, ISplitterType] = {
        "RecursiveCharacterTextSplitterType": RecursiveCharacterTextSplitterType(),
    }

    def __init__(self, registry: Optional[Dict[str, ISplitterType]] = None):
        self._registry = registry or Splitter._DEFAULT_REGISTRY

    def split(self, splitter_type: str, docs: List[Document]) -> List[Document]:
        splitter = self._registry.get(splitter_type)
        if not splitter:
            raise ValueError(f"No splitter for '{splitter_type}'")
        return splitter.split(docs)
