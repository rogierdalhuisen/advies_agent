"""Prompts for the structured retriever pipeline."""

GRADING_PROMPT = (
    "Query: {query}\n\n"
    "Documents:\n{docs_text}\n\n"
    "Classify whether these documents answer the query directly, "
    "indirectly (e.g. explaining why something is excluded), "
    "or not at all (miss)."
)

REWRITE_PROMPT = (
    "The following query did not yield relevant results:\n"
    "Original query: {original_query}\n"
    "Last query tried: {current_query}\n\n"
    "Rewrite the query to improve retrieval. "
    "Return only the rewritten query, nothing else."
)

SUMMARIZE_PROMPT = """\
Je bent een retrieval-specialist voor verzekeringspolisdocumenten.

Je hebt documenten opgehaald over: {aspect}
Voor verzekeraar: {provider}
Productbeschrijving: {product_description}

Opgehaalde documenten:
{docs_text}

Richtlijnen:
- Rapporteer ALLEEN wat de documenten zeggen — citeer of parafraseer relevante clausules
- Interpreteer GEEN dubbelzinnige clausules en maak GEEN aannames
- Trek GEEN conclusies over geschiktheid van het product
- Signaleer onduidelijkheden of vertaalkwesties
- Structureer bevindingen per dekkingsniveau waar de documenten onderscheid maken
- Voeg een overall_summary toe voor bevindingen die gelden voor alle dekkingsniveaus

Rapporteer in het Nederlands. Gebruik originele Engelse termen tussen haakjes bij vakjargon waar de Nederlandse vertaling dubbelzinnig kan zijn.\
"""
