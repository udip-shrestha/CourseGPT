import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document

from API.Repository.chroma_vector_repository import ChromaVectorRepository


@pytest.fixture
def mock_client():
    """
    Fake Chroma client with create_collection(), delete_collection(),
    and get_collection() all mocked.
    """
    return MagicMock()


@pytest.fixture
def repo(mock_client):
    """
    The repository under test.
    """
    return ChromaVectorRepository(client=mock_client)


@pytest.fixture
def mock_collection(mock_client):
    """
    Fake Chroma collection returned by client.get_collection().
    """
    collection = MagicMock()
    mock_client.get_collection.return_value = collection
    return collection


def test_create_collection(repo, mock_client):
    repo.create_collection(
        course_id="course-1",
        embedding_function="embed-fn",
        metric="cosine"
    )

    mock_client.create_collection.assert_called_once_with(
        name="course-1",
        embedding_function="embed-fn",
        metadata={"hnsw:space": "cosine"}
    )


def test_create_collection_no_metric(repo, mock_client):
    repo.create_collection("course-1", embedding_function=None, metric=None)

    mock_client.create_collection.assert_called_once_with(
        name="course-1",
        embedding_function=None,
        metadata=None
    )


def test_delete_collection(repo, mock_client):
    repo.delete_collection("course-1")
    mock_client.delete_collection.assert_called_once_with(name="course-1")


def test_create_index(repo, mock_collection, mock_client):
    docs = [
        Document(page_content="Alpha", metadata={"doc_id": "d1"}),
        Document(page_content="Beta", metadata={"doc_id": "d1"}),
    ]

    repo.create_index("course-1", docs)

    # ensure collection retrieved
    mock_client.get_collection.assert_called_once_with(name="course-1")

    # expected transformed data
    expected_ids = ["d1_0", "d1_1"]
    expected_docs = ["Alpha", "Beta"]
    expected_metadata = [{"doc_id": "d1"}, {"doc_id": "d1"}]

    mock_collection.add.assert_called_once_with(
        ids=expected_ids,
        documents=expected_docs,
        metadatas=expected_metadata
    )


def test_query(repo, mock_collection, mock_client):
    mock_collection.query.return_value = {
        "documents": [["chunk-1", "chunk-2"]],
        "metadatas": [[{"doc_id": "a"}, {"doc_id": "b"}]],
        "distances": [[0.12, 0.55]],
    }

    results = repo.query("course-1", "what is ai?", top_k=2)

    # validate method calls
    mock_client.get_collection.assert_called_once_with(name="course-1")
    mock_collection.query.assert_called_once_with(
        query_texts=["what is ai?"],
        n_results=2
    )

    # validate output format
    assert len(results) == 2

    doc1, score1 = results[0]
    doc2, score2 = results[1]

    # First result
    assert isinstance(doc1, Document)
    assert doc1.page_content == "chunk-1"
    assert doc1.metadata == {"doc_id": "a"}
    assert score1 == 0.12

    # Second result
    assert isinstance(doc2, Document)
    assert doc2.page_content == "chunk-2"
    assert doc2.metadata == {"doc_id": "b"}
    assert score2 == 0.55


def test_delete_index(repo, mock_collection, mock_client):
    repo.delete_index("course-1", document_id="d1")

    mock_client.get_collection.assert_called_once_with(name="course-1")

    mock_collection.delete.assert_called_once_with(
        where={"doc_id": "d1"}
    )
