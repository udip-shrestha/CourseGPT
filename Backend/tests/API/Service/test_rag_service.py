import pytest
from langchain_core.documents import Document
from fastapi import HTTPException
from unittest.mock import MagicMock

from API.Service.rag_service import RAGService


def test_create_index_success(rag_service: RAGService, mock_loader_factory: MagicMock, mock_splitter: MagicMock, mock_vector_repo: MagicMock):
    mock_loader_factory.get.return_value.load.return_value = [Document(page_content="Hello", metadata={})]
    mock_splitter.split_documents.return_value = [
        Document(page_content="Chunk 1", metadata={}),
        Document(page_content="Chunk 2", metadata={}),
    ]

    result = rag_service.create_index("course-123", "doc-1", "lecture1.pdf", "application/pdf", b"bytes")

    mock_loader_factory.get.assert_called_once_with("application/pdf")
    mock_splitter.split_documents.assert_called_once()
    mock_vector_repo.create_index.assert_called_once()

    assert all("doc_id" in c.metadata for c in result)
    assert result[0].metadata["doc_id"] == "doc-1"


def test_create_index_empty_file(rag_service: RAGService, mock_loader_factory: MagicMock):
    mock_loader_factory.get.return_value.load.return_value = []

    with pytest.raises(HTTPException) as exc:
        rag_service.create_index("c1", "d1", "file.pdf", "application/pdf", b"x")

    assert exc.value.status_code == 400
    assert "No text extracted" in exc.value.detail


def test_delete_index_success(rag_service: RAGService, mock_vector_repo: MagicMock):
    rag_service.delete_index("course-1", "doc-1")
    mock_vector_repo.delete_index.assert_called_once_with("course-1", "doc-1")


def test_delete_index_failure(rag_service: RAGService, mock_vector_repo: MagicMock):
    mock_vector_repo.delete_index.side_effect = RuntimeError("ERR")

    with pytest.raises(HTTPException) as exc:
        rag_service.delete_index("c1", "d1")

    assert exc.value.status_code == 500 and "Internal server error" in exc.value.detail


def test_query_success(rag_service: RAGService, mock_rag_strategy_factory: MagicMock):
    mock_strategy = MagicMock()
    mock_strategy.run.return_value = {"answer": "It works", "sources": ["src"]}

    mock_rag_strategy_factory.get.return_value = mock_strategy
    course = {"rag_strategy_id": 1}

    result = rag_service.query("course-1", course, None, "Question?")

    mock_rag_strategy_factory.get.assert_called_once_with("1")
    mock_strategy.run.assert_called_once()
    assert result["answer"] == "It works" and result["sources"] == ["src"]


def test_query_no_results(rag_service: RAGService, mock_rag_strategy_factory: MagicMock):
    mock_strategy = MagicMock()
    mock_strategy.run.return_value = None
    mock_rag_strategy_factory.get.return_value = mock_strategy
    course = {"rag_strategy_id": 1}

    with pytest.raises(HTTPException) as exc:
        rag_service.query("c1", course, None, "Question?")

    assert exc.value.status_code == 404 and "No relevant information" in exc.value.detail

