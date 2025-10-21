import pytest
from unittest.mock import patch, MagicMock
import API.Util.prompt_builders as prompt_builders


def test_prompt_builder_raises_for_unknown_type() -> None:
    """Ensure PromptBuilder raises ValueError for unsupported prompt types."""
    pb = prompt_builders.PromptBuilder()
    with pytest.raises(ValueError, match="Unsupported prompt type"):
        pb.build("UnknownPromptType", "ctx", "question")


def test_prompt_builder_uses_default_registry_entry() -> None:
    """Ensure the DefaultLangChainRAGPrompt builder instance’s build() is called."""
    pb = prompt_builders.PromptBuilder()
    context = "Python functions"
    question = "What is recursion?"

    with patch.object(pb._registry["DefaultLangChainRAGPrompt"], "build", return_value="mock_prompt") as mock_build:
        result = pb.build("DefaultLangChainRAGPrompt", context, question)

        assert result == "mock_prompt"
        mock_build.assert_called_once_with(context, question)


def test_default_langchain_builder_invokes_prompt_template() -> None:
    """Ensure DefaultLangChainRAGPromptBuilder calls its internal prompt_template.invoke()."""
    fake_prompt = MagicMock()
    fake_prompt.invoke.return_value = "generated_prompt"

    with patch.object(prompt_builders.hub, "pull", return_value=fake_prompt) as mock_pull:
        builder = prompt_builders.DefaultLangChainRAGPromptBuilder()
        result = builder.build("ctx", "Why use Python?")

        mock_pull.assert_called_once_with("rlm/rag-prompt")
        fake_prompt.invoke.assert_called_once_with({"context": "ctx", "question": "Why use Python?"})
        assert result == "generated_prompt"
