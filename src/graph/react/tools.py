"""Tool wrappers for the single ReAct agent."""

from langchain_core.tools import tool
from src.agents.retriever import RetrieverAgent


def make_retriever_tool(retriever_agent: RetrieverAgent):
    """Factory that wraps a RetrieverAgent as a LangChain tool."""

    @tool
    def retrieve_documents(query: str, insurance_provider: str) -> str:
        """Retrieve and synthesize information about an insurance product.

        Use this tool to investigate a specific insurance provider's documents.
        It performs a full RAG pipeline (retrieve, rerank, grade, generate) and
        returns a synthesized answer plus the top document excerpts.

        Args:
            query: The question to answer about the insurance product.
            insurance_provider: The provider folder name (e.g. "allianz_care", "oom_wib").

        Returns:
            Synthesized answer with supporting document excerpts.
        """
        result = retriever_agent.invoke(query=query, insurance_provider=insurance_provider)

        answer = result.get("answer", "") if isinstance(result, dict) else result.answer
        documents = result.get("documents", []) if isinstance(result, dict) else result.documents

        # Format top 3 document excerpts as context
        excerpts = []
        for doc in documents[:3]:
            content = doc.page_content if hasattr(doc, "page_content") else str(doc)
            excerpts.append(content[:500])

        output = f"**Answer:**\n{answer}"
        if excerpts:
            output += "\n\n**Supporting excerpts:**\n"
            for i, excerpt in enumerate(excerpts, 1):
                output += f"\n[{i}] {excerpt}\n"

        return output

    return retrieve_documents
