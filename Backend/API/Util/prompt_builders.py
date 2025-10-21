from typing import Protocol, Dict, Optional
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate


class IPromptBuilderType(Protocol):
    """Builds a prompt for the RAG pipeline."""
    def build(self, context: str, question: str) -> ChatPromptTemplate:
        ...


class DefaultLangChainRAGPromptBuilder(IPromptBuilderType):
    """Uses the default LangChain RAG prompt from the Hub."""
    def __init__(self):
        # Load prompt once at init
        self.prompt_template = hub.pull("rlm/rag-prompt")

    def build(self, context: str, question: str) -> ChatPromptTemplate:
        """Return a compiled prompt with provided context and question."""
        return self.prompt_template.invoke({"context": context, "question": question})


class PromptBuilder:
    """Factory that delegates prompt creation by type."""
    _DEFAULT_REGISTRY: Dict[str, IPromptBuilderType] = {
        "DefaultLangChainRAGPrompt": DefaultLangChainRAGPromptBuilder(),
    }

    def __init__(self, registry: Optional[Dict[str, IPromptBuilderType]] = None):
        self._registry = registry or PromptBuilder._DEFAULT_REGISTRY

    def build(self, prompt_type: str, context: str, question: str) -> ChatPromptTemplate:
        """Retrieve the correct builder and create a prompt."""
        builder = self._registry.get(prompt_type)
        if not builder:
            supported = ", ".join(self._registry.keys())
            raise ValueError(f"Unsupported prompt type '{prompt_type}'. Supported types: {supported}")
        return builder.build(context, question)
