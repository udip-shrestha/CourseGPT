import pytest
from langchain_core.documents import Document
from API.Service.rag_service import RAGService
import API.Util.formatters as formatters
from unittest.mock import MagicMock, patch
from fastapi import HTTPException


def test_create_index_success(rag_service: RAGService, mock_loader: MagicMock, mock_splitter: MagicMock, mock_vector_repo: MagicMock) -> None:
    """Should successfully load, split, and store document chunks."""
    mock_loader.load.return_value = [Document(page_content="Hello", metadata={})]
    mock_splitter.split.return_value = [
        Document(page_content="Chunk 1", metadata={}),
        Document(page_content="Chunk 2", metadata={}),
    ]

    result = rag_service.create_index("course-123", "doc-1", "RecursiveSplitter", "lecture1.pdf", "pdf", b"fake-bytes")

    mock_loader.load.assert_called_once_with("lecture1.pdf", "pdf", b"fake-bytes")
    mock_splitter.split.assert_called_once()
    mock_vector_repo.create_index.assert_called_once()
    assert all("doc_id" in chunk.metadata for chunk in result)
    assert result[0].metadata["doc_id"] == "doc-1"


def test_create_index_empty_file(rag_service: RAGService, mock_loader: MagicMock) -> None:
    """Should raise 400 if no text is extracted from file."""
    mock_loader.load.return_value = []

    with pytest.raises(HTTPException) as exc:
        rag_service.create_index("c1", "d1", "RecursiveSplitter", "lecture1.pdf", "pdf", b"fake")

    assert exc.value.status_code == 400
    assert "No text extracted" in exc.value.detail


def test_delete_index_success(rag_service: RAGService, mock_vector_repo: MagicMock) -> None:
    """Should call vector_repo.delete_index with correct arguments."""
    rag_service.delete_index("course-123", "doc-456")

    mock_vector_repo.delete_index.assert_called_once_with("course-123", "doc-456")


def test_query_success(rag_service: RAGService, mock_vector_repo: MagicMock, mock_prompt_builder: MagicMock, mock_llm: MagicMock) -> None:
    """Should retrieve chunks, build prompt, and return formatted answer."""
    mock_vector_repo.query.return_value = [
        (Document(page_content="Python defines scope via indentation.", metadata={"source": "lecture1.pdf"}), 0.1)
    ]
    mock_prompt_builder.build.return_value = "Prompt built successfully"
    mock_llm.invoke.return_value = "Python uses indentation to define scope."

    result = rag_service.query("course-1", "What defines scope in Python?")

    mock_vector_repo.query.assert_called_once_with("course-1", "What defines scope in Python?")
    mock_prompt_builder.build.assert_called_once()
    mock_llm.invoke.assert_called_once()
    assert "answer" in result and "sources" in result
    assert "Python" in result["answer"]
    assert "lecture1.pdf" in result["sources"]


def test_query_no_results(rag_service: RAGService, mock_vector_repo: MagicMock) -> None:
    """Should raise 404 when no relevant information is found."""
    mock_vector_repo.query.return_value = []

    with pytest.raises(HTTPException) as exc:
        rag_service.query("course-1", "What defines scope?")

    assert exc.value.status_code == 404
    assert "No relevant information" in exc.value.detail


def test_delete_index_success(rag_service: RAGService, mock_vector_repo: MagicMock) -> None:
    """Should call vector_repo.delete_index with correct arguments."""
    rag_service.delete_index("course-123", "doc-456")

    mock_vector_repo.delete_index.assert_called_once_with("course-123", "doc-456")


def test_delete_index_failure(rag_service: RAGService, mock_vector_repo: MagicMock) -> None:
    """Should raise HTTPException if vector_repo.delete_index fails."""
    mock_vector_repo.delete_index.side_effect = RuntimeError("Vector deletion error")

    with pytest.raises(HTTPException) as exc:
        rag_service.delete_index("course-1", "doc-1")

    assert exc.value.status_code == 500
    assert "Internal server error" in exc.value.detail


