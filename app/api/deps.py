from app.data.store import get_data_store


def get_store():
    # just return the shared store
    return get_data_store()


