# Save and load custom experiments

import json
import os
from typing import List, Dict, Any

EXPERIMENTS_FILE = "user_experiments.json"

def load_experiments() -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.exists(EXPERIMENTS_FILE):
        return {}
    try:
        with open(EXPERIMENTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_experiment(name: str, steps: List[Dict[str, Any]]):
    experiments = load_experiments()
    experiments[name] = steps
    with open(EXPERIMENTS_FILE, "w") as f:
        json.dump(experiments, f, indent=4)

def get_experiment(name: str):
    experiments = load_experiments()
    return experiments.get(name)
