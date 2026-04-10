import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from API.Util.loaders import (
    LoaderFactory,
    PDFLoader,
    TXTLoader,
    MDLoader,
    HTMLLoader,
    XMLLoader,
    CSVLoader,
    DOCXLoader,
    XLSXLoader,
    PPTXLoader,
    ImageLoader,
    LOADER_CLASS_REGISTRY,
)


# ------------------------------------------------------------
# FACTORY TESTS
# ------------------------------------------------------------

def test_loader_factory_raises_for_unknown_mime_type():
    factory = LoaderFactory()
    with pytest.raises(ValueError): factory.get("nope")


def test_loader_factory_returns_correct_loader_class():
    factory = LoaderFactory()
    assert isinstance(factory.get("PDFLoader"), PDFLoader)
    assert isinstance(factory.get("TXTLoader"), TXTLoader)
    assert isinstance(factory.get("MDLoader"), MDLoader)
    assert isinstance(factory.get("HTMLLoader"), HTMLLoader)
    assert isinstance(factory.get("XMLLoader"), XMLLoader)
    assert isinstance(factory.get("CSVLoader"), CSVLoader)
    assert isinstance(factory.get("DOCXLoader"), DOCXLoader)
    assert isinstance(factory.get("XLSXLoader"), XLSXLoader)
    assert isinstance(factory.get("PPTXLoader"), PPTXLoader)
    assert isinstance(factory.get("ImageLoader"), ImageLoader)


def test_loader_registry_contains_all_loaders():
    assert set(LOADER_CLASS_REGISTRY.keys()) == {
        "PDFLoader","TXTLoader","MDLoader","HTMLLoader",
        "XMLLoader","CSVLoader","DOCXLoader","XLSXLoader","PPTXLoader","ImageLoader"
    }


# ------------------------------------------------------------
# HELPER MOCK
# ------------------------------------------------------------

def _mock_unstructured_loader(mock_class):
    mock_instance = MagicMock()
    mock_instance.load.return_value = [
        Document(page_content="sample text", metadata={"meta": "x"})
    ]
    mock_class.return_value = mock_instance
    return mock_instance


# ------------------------------------------------------------
# PARAMETRIZED TEST – patch correct local import targets
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "loader_class, patch_path",
    [
        (PDFLoader, "API.Util.loaders.UnstructuredPDFLoader"),
        (TXTLoader, "API.Util.loaders.TextLoader"),
        (MDLoader, "API.Util.loaders.UnstructuredMarkdownLoader"),
        (HTMLLoader, "API.Util.loaders.UnstructuredHTMLLoader"),
        (XMLLoader, "API.Util.loaders.UnstructuredXMLLoader"),
        (CSVLoader, "API.Util.loaders.UnstructuredCSVLoader"),
        (DOCXLoader, "API.Util.loaders.UnstructuredWordDocumentLoader"),
        (XLSXLoader, "API.Util.loaders.UnstructuredExcelLoader"),
        (PPTXLoader, "API.Util.loaders.UnstructuredPowerPointLoader"),
    ],
)
def test_each_loader_calls_unstructured_loader_and_returns_documents(loader_class, patch_path):
    loader = loader_class()

    with patch(patch_path) as mock_class:
        mock_instance = _mock_unstructured_loader(mock_class)
        docs = loader.load("file.ext", b"xyz")

    mock_class.assert_called_once()
    mock_instance.load.assert_called_once()
    assert len(docs) == 1
    assert docs[0].page_content == "sample text"
    assert docs[0].metadata["source"] == "file.ext"


# ------------------------------------------------------------
# INDIVIDUAL LOADER TESTS
# ------------------------------------------------------------

def _mock_loader(path):
    patcher = patch(path)
    mock_class = patcher.start()
    mock_inst = MagicMock()
    mock_inst.load.return_value = [Document(page_content="sample", metadata={})]
    mock_class.return_value = mock_inst
    return patcher, mock_inst


def test_pdf_loader():
    p, m = _mock_loader("API.Util.loaders.UnstructuredPDFLoader")
    docs = PDFLoader().load("a.pdf", b"x"); p.stop()
    m.load.assert_called_once(); assert docs[0].metadata["source"] == "a.pdf"


def test_txt_loader():
    p, m = _mock_loader("API.Util.loaders.TextLoader")
    docs = TXTLoader().load("a.txt", b"x"); p.stop()
    m.load.assert_called_once(); assert docs[0].metadata["source"] == "a.txt"


def test_md_loader():
    p, m = _mock_loader("API.Util.loaders.UnstructuredMarkdownLoader")
    docs = MDLoader().load("a.md", b"x"); p.stop()
    m.load.assert_called_once(); assert docs[0].metadata["source"] == "a.md"


def test_html_loader():
    p, m = _mock_loader("API.Util.loaders.UnstructuredHTMLLoader")
    docs = HTMLLoader().load("a.html", b"x"); p.stop()
    m.load.assert_called_once(); assert docs[0].metadata["source"] == "a.html"


def test_xml_loader():
    p, m = _mock_loader("API.Util.loaders.UnstructuredXMLLoader")
    docs = XMLLoader().load("a.xml", b"x"); p.stop()
    m.load.assert_called_once(); assert docs[0].metadata["source"] == "a.xml"


def test_csv_loader():
    p, m = _mock_loader("API.Util.loaders.UnstructuredCSVLoader")
    docs = CSVLoader().load("a.csv", b"x"); p.stop()
    m.load.assert_called_once(); assert docs[0].metadata["source"] == "a.csv"


def test_docx_loader():
    p, m = _mock_loader("API.Util.loaders.UnstructuredWordDocumentLoader")
    docs = DOCXLoader().load("a.docx", b"x"); p.stop()
    m.load.assert_called_once(); assert docs[0].metadata["source"] == "a.docx"


def test_xlsx_loader():
    p, m = _mock_loader("API.Util.loaders.UnstructuredExcelLoader")
    docs = XLSXLoader().load("a.xlsx", b"x"); p.stop()
    m.load.assert_called_once(); assert docs[0].metadata["source"] == "a.xlsx"


def test_pptx_loader():
    p, m = _mock_loader("API.Util.loaders.UnstructuredPowerPointLoader")
    docs = PPTXLoader().load("a.pptx", b"x"); p.stop()
    m.load.assert_called_once(); assert docs[0].metadata["source"] == "a.pptx"
