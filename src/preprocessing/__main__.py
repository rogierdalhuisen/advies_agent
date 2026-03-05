"""Allow running as: python -m src.preprocessing"""

from .preprocessor import preprocess_user
from .orchestrator_input import prepare_orchestrator_input

if __name__ == "__main__":
    user = preprocess_user(aanvraag_id=92)
    print(f"User: {user.aanvraag_id} — {user.bestemming_land}")
    print(f"Wants ZKV: {user.wants_zkv}")
    print(f"Premiums for {len(user.premiums)} providers")

    inputs = prepare_orchestrator_input(user)
    print(f"Orchestrator input keys: {list(inputs.keys())}")
    print(f"Available providers: {inputs['available_providers']}")
