import os
import shutil
from typing import Protocol, List, Dict, Type, Optional, runtime_checkable
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader, UnstructuredExcelLoader, UnstructuredHTMLLoader, UnstructuredMarkdownLoader, UnstructuredPowerPointLoader, UnstructuredWordDocumentLoader, UnstructuredXMLLoader, UnstructuredCSVLoader, UnstructuredImageLoader
from fastapi import HTTPException, status
import unstructured_pytesseract.pytesseract as pytesseract
from API.Util.files import create_temp_file_from_bytes


@runtime_checkable
class ILoader(Protocol):
    """Extracts LangChain Documents from raw bytes."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        ...


class PDFLoader(ILoader):
    """Loads text from PDF bytes."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in UnstructuredPDFLoader(str(path)).load()
            ]


class TXTLoader(ILoader):
    """Loads text from .txt bytes."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in TextLoader(str(path), autodetect_encoding=True).load()
            ]


class MDLoader(ILoader):
    """Loads text from Markdown (.md) bytes."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in UnstructuredMarkdownLoader(str(path)).load()
            ]


class HTMLLoader(ILoader):
    """Loads text from HTML using Unstructured's HTML parser."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in UnstructuredHTMLLoader(str(path)).load()
            ]


class XMLLoader(ILoader):
    """Loads XML content using UnstructuredXMLLoader."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in UnstructuredXMLLoader(str(path)).load()
            ]


class CSVLoader(ILoader):
    """Loads CSV files."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in UnstructuredCSVLoader(str(path)).load()
            ]


class DOCXLoader(ILoader):
    """Loads text from DOCX files using Unstructured."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in UnstructuredWordDocumentLoader(str(path)).load()
            ]

class XLSXLoader(ILoader):
    """Loads text from XLSX spreadsheets using Unstructured."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in UnstructuredExcelLoader(str(path)).load()
            ]


class PPTXLoader(ILoader):
    """Loads text from PowerPoint (PPTX) using Unstructured."""
    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in UnstructuredPowerPointLoader(str(path)).load()
            ]


class ImageLoader(ILoader):
    """Extracts OCR/text content from supported image files."""
    def __init__(self) -> None:
        self._configure_tesseract()

    def _configure_tesseract(self) -> None:
        candidates = [
            os.environ.get("TESSERACT_CMD"),
            shutil.which("tesseract"),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]

        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                pytesseract.tesseract_cmd = candidate
                return

        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Image OCR is not available on this server because Tesseract is not installed. "
                "Please install Tesseract OCR and restart the backend."
            ),
        )

    def load(self, file_name: str, file_bytes: bytes) -> List[Document]:
        with create_temp_file_from_bytes(file_name, file_bytes) as path:
            return [
                Document(page_content=doc.page_content, metadata={**doc.metadata, "source": file_name})
                for doc in UnstructuredImageLoader(str(path), mode="elements").load()
            ]


LOADER_CLASS_REGISTRY: Dict[str, Type[ILoader]] = {
    "PDFLoader": PDFLoader,
    "TXTLoader": TXTLoader,
    "MDLoader": MDLoader,
    "HTMLLoader": HTMLLoader,
    "XMLLoader": XMLLoader,
    "CSVLoader": CSVLoader,
    "DOCXLoader": DOCXLoader,
    "XLSXLoader": XLSXLoader,
    "PPTXLoader": PPTXLoader,
    "ImageLoader": ImageLoader,
}


class LoaderFactory:
    """Factory to retrieve a loader instance based on MIME type."""

    def __init__(self, registry: Optional[Dict[str, object]] = None):
        self._registry = registry or LOADER_CLASS_REGISTRY.copy()

    def get(self, mime_type: str) -> ILoader:
        mime_type = str(mime_type)
        if mime_type not in self._registry:
            raise ValueError(f"No loader registered for MIME type '{mime_type}'")

        loader = self._registry[mime_type]
        return loader() if isinstance(loader, type) else loader

