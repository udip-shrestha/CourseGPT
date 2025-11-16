import pytest
from unittest.mock import patch, MagicMock

from API.Util.rag_strategy import RAGStrategyFactory, SimpleRAGStrategy, AgenticRAGStrategy


@pytest.fixture
def rag_factory():
    """Provide a RAGStrategyFactory for tests."""
    return RAGStrategyFactory()


def test_rag_strategy_factory_raises_for_unknown_type(rag_factory):
    """Ensure RAGStrategyFactory raises ValueError for unsupported strategy IDs."""
    with pytest.raises(ValueError, match="Unknown RAG strategy id"):
        rag_factory.get("NonExistentStrategy")


def test_rag_strategy_factory_returns_correct_strategy(rag_factory):
    """Ensure RAGStrategyFactory returns valid strategy objects for known keys."""
    simple = rag_factory.get("SimpleRAGStrategy")
    agentic = rag_factory.get("AgenticRAGStrategy")

    assert isinstance(simple, SimpleRAGStrategy)
    assert isinstance(agentic, AgenticRAGStrategy)


def test_simple_rag_strategy_calls_all_internal_steps():
    """Ensure SimpleRAGStrategy.run calls the expected internal methods in order."""
    strategy = SimpleRAGStrategy()

    mock_vector = MagicMock()
    mock_sql = MagicMock()
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="Final answer")

    with patch.object(strategy, "retrieve_chunks", return_value=("chunks", ["src"])) as m_chunks, \
        patch.object(strategy, "load_past_messages", return_value=("past", [])) as m_past, \
        patch.object(strategy, "get_course_details", return_value=("meta", {})) as m_meta, \
        patch.object(strategy, "clean_llm_output", return_value="Final answer") as m_clean:

        result = strategy.run(
            mock_vector,
            mock_sql,
            mock_llm,
            "course1",
            {"title": "Course"},
            "student1",
            "What is X?",
        )

    assert result["answer"] == "Final answer"
    assert result["sources"] == ["src"]

    m_chunks.assert_called_once()
    m_past.assert_called_once()
    m_meta.assert_called_once()
    mock_llm.invoke.assert_called_once()
    m_clean.assert_called_once()
    mock_sql.create_query.assert_called_once()


def test_simple_rag_strategy_returns_no_sources_when_insufficient():
    """Ensure SimpleRAGStrategy returns empty source list when insufficient info."""
    strategy = SimpleRAGStrategy()

    mock_vector = MagicMock()
    mock_sql = MagicMock()
    mock_llm = MagicMock()

    with patch.object(strategy, "retrieve_chunks", return_value=("none", [])), \
        patch.object(strategy, "load_past_messages", return_value=("", [])), \
        patch.object(strategy, "get_course_details", return_value=("meta", {})), \
        patch.object(strategy, "clean_llm_output", return_value="I don’t have enough course information to answer that."):

        result = strategy.run(
            mock_vector,
            mock_sql,
            mock_llm,
            "course1",
            {"title": "Course"},
            "student1",
            "What is X?",
        )

    assert result["sources"] == []
    mock_sql.create_query.assert_called_once()


def test_agentic_rag_strategy_uses_create_agent_and_saves_query():
    """Ensure AgenticRAGStrategy uses create_agent and stores the result."""
    strategy = AgenticRAGStrategy()

    mock_vector = MagicMock()
    mock_sql = MagicMock()
    mock_llm = MagicMock()

    fake_stream = [
        {"model": {"messages": [MagicMock(content="Final answer")]}},
    ]

    with patch("API.Util.rag_strategy.create_agent") as m_agent, \
         patch.object(strategy, "clean_llm_output", return_value="Final answer") as m_clean:

        m_agent.return_value.stream.return_value = fake_stream

        result = strategy.run(
            mock_vector,
            mock_sql,
            mock_llm,
            "course1",
            {"title": "Course"},
            "student1",
            "What is recursion?",
        )

    assert result["answer"] == "Final answer"
    m_agent.assert_called_once()
    m_clean.assert_called()
    mock_sql.create_query.assert_called_once()


def test_agentic_rag_strategy_no_sources_when_insufficient():
    """Ensure AgenticRAGStrategy returns no sources when insufficient info."""
    strategy = AgenticRAGStrategy()

    mock_vector = MagicMock()
    mock_sql = MagicMock()
    mock_llm = MagicMock()

    fake_stream = [
        {"model": {"messages": [MagicMock(content="I don’t have enough course information to answer that.")]}}
    ]

    with patch("API.Util.rag_strategy.create_agent") as m_agent, \
         patch.object(strategy, "clean_llm_output", return_value="I don’t have enough course information to answer that."):

        m_agent.return_value.stream.return_value = fake_stream

        result = strategy.run(
            mock_vector,
            mock_sql,
            mock_llm,
            "course1",
            {"title": "Course"},
            "student1",
            "What is recursion?",
        )

    assert result["sources"] == []
    mock_sql.create_query.assert_called_once()
