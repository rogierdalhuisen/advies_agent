"""
Example of how to use the custom retrieval tools with LangChain.

This demonstrates the factory pattern for creating tools that work with
an existing QdrantVectorStore instance.
"""

from pydantic import SecretStr
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from qdrant_client import QdrantClient

from src.config import QDRANT_HOST, OPENAI_API_KEY
from src.retrieval.custom_tools import (
    create_company_search_tool,
    create_company_hybrid_search_tool,
    create_all_companies_dense_search_tool,
    create_all_companies_hybrid_search_tool,
)


def main():
    """Example usage of custom retrieval tools."""

    # 1. Initialize your vector store (only once!)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=SecretStr(OPENAI_API_KEY) if OPENAI_API_KEY else None
    )
    sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

    client = QdrantClient(host=QDRANT_HOST)

    vector_store = QdrantVectorStore(
        client=client,
        collection_name="dekkingen",
        embedding=embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.DENSE,
        vector_name="dense",
        sparse_vector_name="sparse",
    )

    # 2. Create tools using factory functions (pass the vector_store)
    # Company-specific tools
    company_dense_tool = create_company_search_tool(vector_store)
    company_hybrid_tool = create_company_hybrid_search_tool(vector_store)

    # All companies tools
    all_dense_tool = create_all_companies_dense_search_tool(vector_store)
    all_hybrid_tool = create_all_companies_hybrid_search_tool(vector_store)

    # 3. Use the tools with bind_tools
    llm = ChatOpenAI(model="gpt-4")
    llm_with_tools = llm.bind_tools([
        company_dense_tool,
        company_hybrid_tool,
        all_dense_tool,
        all_hybrid_tool
    ])

    # 4. Now the LLM can use the tools!
    response = llm_with_tools.invoke(
        "What does Goudse cover for kidney problems?"
    )

    print(response)

    # Alternative: Use tools directly (without LLM)
    print("\n--- Direct tool usage examples ---")

    # Example 1: Company-specific dense search
    print("\n1. Company-specific dense search:")
    result1 = company_dense_tool.invoke({
        "query": "kidney dialysis",
        "company": "Goudse",
        "k": 3
    })
    print(f"Found {len(result1)} results")

    # Example 2: Company-specific hybrid search
    print("\n2. Company-specific hybrid search:")
    result2 = company_hybrid_tool.invoke({
        "query": "kidney dialysis",
        "company": "Goudse",
        "k": 3
    })
    print(f"Found {len(result2)} results")

    # Example 3: All companies dense search
    print("\n3. All companies dense search:")
    result3 = all_dense_tool.invoke({
        "query": "pregnancy coverage",
        "k": 5
    })
    print(f"Found {len(result3)} results from companies:")
    for doc, score in result3:
        print(f"  - {doc.metadata.get('company')}: {score:.4f}")

    # Example 4: All companies hybrid search
    print("\n4. All companies hybrid search:")
    result4 = all_hybrid_tool.invoke({
        "query": "cancer treatment",
        "k": 5
    })
    print(f"Found {len(result4)} results from companies:")
    for doc, score in result4:
        print(f"  - {doc.metadata.get('company')}: {score:.4f}")


if __name__ == "__main__":
    main()
