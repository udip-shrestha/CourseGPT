from typing import Protocol, List, Dict, Type, Optional
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ISplitterType(Protocol):
    """Splits documents into smaller text chunks."""
    def split(self, docs: List[Document]) -> List[Document]:
        ...


class RecursiveSplitterType(ISplitterType):
    """Splits documents using RecursiveCharacterTextSplitter."""
    def split(self, docs: List[Document]) -> List[Document]:
        return RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)


class Splitter:
    """Factory that delegates document splitting by type."""
    _DEFAULT_REGISTRY: Dict[str, Type[ISplitterType]] = {
        "RecursiveSplitterType": RecursiveSplitterType,
    }

    def __init__(self, registry: Optional[Dict[str, Type[ISplitterType]]] = None):
        self._registry = registry or Splitter._DEFAULT_REGISTRY

    def split(self, splitter_type: str, docs: List[Document]) -> List[Document]:
        splitter_cls = self._registry.get(splitter_type)
        if not splitter_cls:
            raise ValueError(f"No splitter for '{splitter_type}'")
        return splitter_cls().split(docs)
