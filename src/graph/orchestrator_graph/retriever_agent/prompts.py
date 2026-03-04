"""Prompts for the structured retriever pipeline."""

VERIFY_PROMPT = (
    "You are a document-relevance verifier for insurance policy retrieval.\n\n"
    "Query: {query}\n\n"
    "Documents:\n{docs_text}\n\n"
    "Classify the documents into one of three categories:\n"
    "- **complete**: The documents fully answer the query. All requested information is present.\n"
    "- **partial**: The documents answer part of the query, but some information is missing. "
    "Mention the part of the query that is still missing in the `missing_info` field.\n"
    "- **miss**: The documents are mostly irrelevant to the query and do not provide useful information.\n\n"
    "Be strict: only classify as 'complete' if the query is thoroughly answered. "
    "If there are gaps, classify as 'partial' and specify what is missing."
)

REWRITE_PROMPT = (
    "The following query returned only partial results from an insurance document retrieval system.\n\n"
    "Original query: {original_query}\n"
    "Last query tried: {current_query}\n"
    "The following information is still missing: {missing_info}\n\n"
    "Rewrite the query to specifically target the missing part. "
    "Return only the rewritten query, should be approximately the same length as the original query"
)

SUMMARIZE_PROMPT = """\
Je bent een retrieval-specialist voor verzekeringspolisdocumenten.

Je hebt documenten opgehaald over: {aspect}
Voor verzekeraar: {provider}
Productbeschrijving: {product_description}

Evaluatiestatus: {evaluation_status}

Opgehaalde documenten:
{docs_text}

Richtlijnen:
- Beantwoord ALLEEN de query en ALLEEN op basis van wat de documenten zeggen
- Interpreteer GEEN dubbelzinnige clausules en maak GEEN aannames
- Trek GEEN conclusies over geschiktheid van het product
- Structureer bevindingen per dekkingsniveau waar de documenten onderscheid maken
- Zie geen belangrijke informatie over het hoofd; maar wees niet te gedetailleerd, hou het redelijk kort
- Voeg een overall_summary toe voor bevindingen die gelden voor alle dekkingsniveaus
- Als de evaluatiestatus "miss" is, vermeld dan duidelijk in de overall_summary en \
information_not_found dat de gevraagde informatie niet is gevonden in de beschikbare documenten

Rapporteer in het Nederlands. Hanteer uiterste precisie bij het vertalen van Engels naar Nederlands; \
wees alert op dubbelzinnigheden in de brontekst en zorg dat de context correct behouden blijft om foutieve interpretaties te voorkomen.\
"""
