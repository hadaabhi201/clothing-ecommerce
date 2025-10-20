from threading import Lock

from tinydb import TinyDB

DB_PATH = "inventory_service/db/inventory_db.json"
_db = None
_lock = Lock()


def get_db() -> TinyDB:
    global _db
    if _db is None:
        with _lock:
            if _db is None:
                _db = TinyDB(DB_PATH)
    return _db
