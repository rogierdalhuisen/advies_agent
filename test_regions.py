import sys
from src.database.data_preprocessor import preprocess_user
from src.graph.orchestrator_graph.preprocessing import prepare_orchestrator_input

user = preprocess_user(92)
print("bestemming_land:", user.bestemming_land)
inputs = prepare_orchestrator_input(user)
print("regions:", inputs['regions'])
