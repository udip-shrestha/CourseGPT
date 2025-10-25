from typing import Protocol, List, Dict, Type, Optional
from langchain.schema import Document
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from API.Util.files import create_temp_file_from_bytes


class ILoaderType(Protocol):
    """Extracts LangChain Documents from raw bytes."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        ...


class PDFLoaderType(ILoaderType):
    """Loads text from PDF bytes."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(".pdf", file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in PyPDFLoader(str(path)).load()
            ]


class DocxLoaderType(ILoaderType):
    """Loads text from DOCX bytes."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(".docx", file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in Docx2txtLoader(str(path)).load()
            ]


class Loader:
    """Factory that delegates file loading by type."""
    _DEFAULT_REGISTRY: Dict[str, ILoaderType] = {
        "pdf": PDFLoaderType(),
        "docx": DocxLoaderType(),
    }

    def __init__(self, registry: Optional[Dict[str, ILoaderType]] = None):
        self._registry = registry or Loader._DEFAULT_REGISTRY

    def load(self, file_name: str, file_type: str, file_bytes: bytes) -> List[Document]:
        loader = self._registry.get(file_type)
        if not loader:
            raise ValueError(f"No loader for '{file_type}'")
        return loader.load(file_name, file_bytes)
