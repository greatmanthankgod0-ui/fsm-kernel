from .storage import load_store, save_store

STORE = load_store()


def get_session(user_id):
    return STORE.get(str(user_id), {})


def set_session(user_id, session):
    STORE[str(user_id)] = session
    save_store(STORE)
