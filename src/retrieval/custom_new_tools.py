from langchain_core.tools import tool
from src.retrieval.retriever import retriever  # Import your instance

@tool
def retrieve_insurance_docs(query: str, company: str) -> str:
    """
    Search for insurance documents. specific to a company. 
    Useful when you need to find policy details, coverage, or exclusions.
    """
    # 1. Call your custom class
    results = retriever.search_company(query, company)
    
    # 2. Format the raw output into a string for the LLM
    formatted_results = [
        retriever.format_document_with_context(doc) for doc, score in results
    ]
    
    return "\n\n".join(formatted_results)