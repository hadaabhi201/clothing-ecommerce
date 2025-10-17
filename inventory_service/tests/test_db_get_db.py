
import inventory_service.db.init as dbinit

def test_get_db_with_patch(tmp_path, monkeypatch):
    test_file = tmp_path / "test.json"
    monkeypatch.setattr(dbinit, "DB_PATH", str(test_file))

    # reset singleton
    dbinit._db = None

    db1 = dbinit.get_db()
    db2 = dbinit.get_db()

    assert db1 is db2
    assert db1.storage._handle.name.endswith("test.json")