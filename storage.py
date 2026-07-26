import json
import os

DB_PATH = "kernel/session_store.json"


def load_store():
    if not os.path.exists(DB_PATH):
        return {}

    with open(DB_PATH, "r") as f:
        return json.load(f)


def save_store(store):
    with open(DB_PATH, "w") as f:
        json.dump(store, f, indent=2)
