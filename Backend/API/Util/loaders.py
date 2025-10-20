from typing import Protocol, List, Dict, Type, Optional
from langchain.schema import Document
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from API.Util.files import create_temp_file_from_bytes


class ILoaderType(Protocol):
    """Extracts LangChain Documents from raw bytes."""
    def load(self, file_bytes: bytes) -> List[Document]:
        ...


class PDFLoaderType(ILoaderType):
    """Loads text from PDF bytes."""
    def load(self, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(".pdf", file_bytes) as path:
            return PyPDFLoader(str(path)).load()


class DocxLoaderType(ILoaderType):
    """Loads text from DOCX bytes."""
    def load(self, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(".docx", file_bytes) as path:
            return Docx2txtLoader(str(path)).load()


class Loader:
    """Factory that delegates file loading by type."""
    _DEFAULT_REGISTRY: Dict[str, Type[ILoaderType]] = {
        "pdf": PDFLoaderType,
        "docx": DocxLoaderType,
    }

    def __init__(self, registry: Optional[Dict[str, Type[ILoaderType]]] = None):
        self._registry = registry or Loader._DEFAULT_REGISTRY

    def load(self, file_type: str, file_bytes: bytes) -> List[Document]:
        loader_cls = self._registry.get(file_type)
        if not loader_cls:
            raise ValueError(f"No loader for '{file_type}'")
        return loader_cls().load(file_bytes)
