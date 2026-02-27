"""Node functions for the self-reflective RAG retriever graph."""

import json
import logging
from typing import Literal
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

from src.retrieval.retriever import InsuranceRetriever
from src.retrieval.reranker.reranker import Reranker
from .state import RetrieverState


class GradeResult(BaseModel):
    """3-way classification of document relevance."""

    status: Literal["direct", "indirect", "miss"] = Field(
        description=(
            "direct: docs answer the query directly. "
            "indirect: docs explain why something is excluded or answer indirectly. "
            "miss: docs do not answer the query at all."
        )
    )


def make_retrieve(retriever: InsuranceRetriever):
    def retrieve(state: RetrieverState) -> dict:
        query = state.current_query or state.original_query
        results = retriever.retrieve_company_docs(query, state.insurance_provider, k=state.k)
        return {"documents": [doc for doc, _ in results], "current_query": query}
    return retrieve


def make_rerank(reranker: Reranker):
    def rerank(state: RetrieverState) -> dict:
        return {"documents": reranker.rerank(state.current_query, state.documents, top_n=state.top_n)}
    return rerank


def make_grade(retriever: InsuranceRetriever, llm):
    def grade(state: RetrieverState) -> dict:
        docs_text = "\n---\n".join(
            retriever.format_document_with_context(doc) for doc in state.documents
        )
        result = llm.with_structured_output(GradeResult).invoke(
            f"Query: {state.current_query}\n\n"
            f"Documents:\n{docs_text}\n\n"
            "Classify whether these documents answer the query directly, "
            "indirectly (e.g. explaining why something is excluded), "
            "or not at all (miss)."
        )
        return {"evaluation_status": result.status}
    return grade


def make_rewrite(llm):
    def rewrite(state: RetrieverState) -> dict:
        msg = llm.invoke(
            f"The following query did not yield relevant results:\n"
            f"Original query: {state.original_query}\n"
            f"Last query tried: {state.current_query}\n\n"
            f"Rewrite the query to improve retrieval. "
            f"Return only the rewritten query, nothing else."
        )
        return {"current_query": msg.content.strip(), "retries": state.retries + 1}
    return rewrite


# def make_route(llm, tools):
#     """Router node: uses LLM tool-calling to decide pricing vs retrieval."""
#     llm_with_tools = llm.bind_tools(tools)

#     def route(state: RetrieverState) -> dict:
#         response = llm_with_tools.invoke(state.original_query)

#         if response.tool_calls:
#             tool_call = response.tool_calls[0]
#             # Inject the known provider from state instead of relying on the LLM
#             tool_call["args"]["insurance_providers"] = [state.insurance_provider]
#             logger.info("Calculator tool called with args: %s", json.dumps(tool_call["args"], ensure_ascii=False))
#             result = tools[0].invoke(tool_call["args"])
#             logger.info("Calculator tool result: %s", result)
#             return {"premium_data": result}

#         logger.info("No tool call made by routing LLM")
#         return {"premium_data": ""}

#     return route


def make_generate(retriever: InsuranceRetriever, llm):
    def generate(state: RetrieverState) -> dict:
        docs_text = "\n---\n".join(
            retriever.format_document_with_context(doc) for doc in state.documents
        )
        
        # System Instructions for a "Synthesized but Strict" answer
        base_instructions = (
            "SYSTEM ROLE: You are a strict Insurance Policy Expert.\n"
            "GOAL: Provide a direct, cohesive answer to the user's query using ONLY the provided documents.\n"
            "LANGUAGE: Answer in the same language as the User Query.\n"
            "STRICT RULES:\n"
            "- NO ASSUMPTIONS: Do not say 'This likely means...' or 'Therefore, you are covered.'\n"
            "- NO FORMATTING OVERLOAD: Do not simply list sections. Write a clear, professional answer.\n"
            "- TERMINOLOGY: If a specific term is crucial (e.g., 'Extreme Sports'), keep the original term or put it in parentheses after the translation.\n"
            "- VERBATIM: Use the exact conditions and exclusions found in the text.\n"
            "- RELEVANCY: If a document is not relevant to the specific question, ignore it.\n"
        )

        prompt = f"{base_instructions}\n"
        prompt += f"USER QUERY: {state.original_query}\n\n"
        prompt += f"PROVIDED POLICY DOCUMENTS:\n{docs_text}\n\n"

        if state.evaluation_status == "direct":
            prompt += (
                "TASK: Answer the query directly. Start with the most relevant fact. "
                "Quote the specific conditions or exclusions exactly as written in the documents "
                "to support the answer. Do not add a concluding summary or personal advice."
            )
        else:
            prompt += (
                "TASK: The documents do not contain a direct answer. Provide a brief response "
                "explaining what the documents *do* say regarding this topic, without "
                "stretching the information to fit the query."
            )

        prompt += "\n\nFINAL ANSWER:"

        response = llm.invoke(prompt)
        text = response.content
        
        if isinstance(text, list):
            text = "".join(block["text"] for block in text if block.get("type") == "text")
            
        return {"answer": text.strip()}
        
    return generate
