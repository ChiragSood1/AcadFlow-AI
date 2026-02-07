class DataStore:
    # very simple in-memory store for all data
    def __init__(self):
        self.attendance = None
        self.marks = None
        self.pdf_corpus = {}

    def has_minimum_data(self):
        return self.attendance is not None and self.marks is not None


_store = None


def get_data_store():
    # return one shared instance of DataStore
    global _store
    if _store is None:
        _store = DataStore()
    return _store

