import pytest
from langchain_core.documents import Document
from fastapi import HTTPException
from unittest.mock import MagicMock

from API.Service.rag_service import RAGService


def test_create_index_success(rag_service: RAGService, mock_loader: MagicMock, mock_splitter: MagicMock, mock_vector_repo: MagicMock):
    mock_loader.load.return_value = [Document(page_content="Hello", metadata={})]
    mock_splitter.split.return_value = [
        Document(page_content="Chunk 1", metadata={}),
        Document(page_content="Chunk 2", metadata={}),
    ]

    result = rag_service.create_index("course-123", "doc-1", "RecursiveSplitter", "lecture1.pdf", "pdf", b"bytes")

    mock_loader.load.assert_called_once_with("lecture1.pdf", "pdf", b"bytes")
    mock_splitter.split.assert_called_once()
    mock_vector_repo.create_index.assert_called_once()

    assert all("doc_id" in c.metadata for c in result)
    assert result[0].metadata["doc_id"] == "doc-1"


def test_create_index_empty_file(rag_service: RAGService, mock_loader: MagicMock):
    mock_loader.load.return_value = []

    with pytest.raises(HTTPException) as exc:
        rag_service.create_index("c1", "d1", "RecursiveSplitter", "file.pdf", "pdf", b"x")

    assert exc.value.status_code == 400
    assert "No text extracted" in exc.value.detail


def test_delete_index_success(rag_service: RAGService, mock_vector_repo: MagicMock):
    rag_service.delete_index("course-123", "doc-456")
    mock_vector_repo.delete_index.assert_called_once_with("course-123", "doc-456")


def test_delete_index_failure(rag_service: RAGService, mock_vector_repo: MagicMock):
    mock_vector_repo.delete_index.side_effect = RuntimeError("ERR")

    with pytest.raises(HTTPException) as exc:
        rag_service.delete_index("c1", "d1")

    assert exc.value.status_code == 500
    assert "Internal server error" in exc.value.detail


def test_query_success(rag_service: RAGService, mock_rag_strategy_factory: MagicMock):
    # Mock strategy
    mock_strategy = MagicMock()
    mock_strategy.run.return_value = {
        "answer": "Python uses indentation to define scope.",
        "sources": ["lecture1.pdf"]
    }

    mock_rag_strategy_factory.get.return_value = mock_strategy

    course = {"rag_strategy_id": 1}
    result = rag_service.query("course-1", course, None, "What defines scope?")

    mock_rag_strategy_factory.get.assert_called_once_with("1")
    mock_strategy.run.assert_called_once()

    assert "answer" in result
    assert "Python" in result["answer"]
    assert "lecture1.pdf" in result["sources"][0]


def test_query_no_results(rag_service: RAGService, mock_rag_strategy_factory: MagicMock):
    mock_strategy = MagicMock()
    mock_strategy.run.return_value = None

    mock_rag_strategy_factory.get.return_value = mock_strategy

    course = {"rag_strategy_id": 1}

    with pytest.raises(HTTPException) as exc:
        rag_service.query("c1", course, None, "What defines scope?")

    assert exc.value.status_code == 404
    assert "No relevant information" in exc.value.detail
