"""Configuration and agent registry for the Chainlit frontend."""

from chainlit.input_widget import Select

from src.agents.retriever import RetrieverAgent
from src.agents.comparer import ComparerAgent

INSURANCE_PROVIDERS = [
    "allianz_care",
    "allianz_globetrotter",
    "cigna_close_care",
    "cigna_global_care",
    "expatriate_group",
    "globality_yougenio",
    "goudse_expat_pakket",
    "goudse_ngo_zendelingen",
    "goudse_working_nomad",
    "oom_tib",
    "oom_wib",
    "special_isis",
]

DEFAULT_PROVIDER_INDEX = 0

AGENTS = {
    "retriever": {
        "class": RetrieverAgent,
        "build_widgets": lambda: [
            Select(
                id="provider",
                label="Insurance Provider",
                values=INSURANCE_PROVIDERS,
                initial_index=DEFAULT_PROVIDER_INDEX,
            ),
        ],
        "build_inputs": lambda query, session: {
            "original_query": query,
            "insurance_provider": session.get("provider"),
        },
        "output_key": "answer",
    },
    "comparer": {
        "class": ComparerAgent,
        "build_widgets": lambda: [
            Select(
                id="provider_1",
                label="Provider 1",
                values=INSURANCE_PROVIDERS,
                initial_index=0,
            ),
            Select(
                id="provider_2",
                label="Provider 2",
                values=INSURANCE_PROVIDERS,
                initial_index=1,
            ),
            Select(
                id="provider_3",
                label="Provider 3 (optional)",
                values=["none"] + INSURANCE_PROVIDERS,
                initial_index=0,
            ),
        ],
        "build_inputs": lambda query, session: {
            "original_query": query,
            "insurance_providers": [
                p for p in [
                    session.get("provider_1"),
                    session.get("provider_2"),
                    session.get("provider_3"),
                ] if p and p != "none"
            ],
        },
        "output_key": "comparison",
    },
}

DEFAULT_AGENT = "retriever"
AGENT_NAMES = list(AGENTS.keys())
