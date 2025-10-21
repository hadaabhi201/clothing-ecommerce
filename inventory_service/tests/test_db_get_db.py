from pathlib import Path

import pytest
from tinydb import TinyDB

import inventory_service.db.init as dbinit


def test_get_db_with_patch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    test_file = tmp_path / "test.json"
    monkeypatch.setattr(dbinit, "DB_PATH", str(test_file))

    dbinit._db = None  # reset singleton

    db1 = dbinit.get_db()
    db2 = dbinit.get_db()

    assert db1 is db2
    assert isinstance(db1, TinyDB)
    assert test_file.exists()
