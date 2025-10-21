import pytest
from tinydb import TinyDB

from inventory_service.core.db_init import init_inventory
from inventory_service.models import CategoryWithItems


def test_init_inventory(monkeypatch: pytest.MonkeyPatch) -> None:
    tmp_db = TinyDB("test_inventory.json")
    # Patch the function used by the code under test
    monkeypatch.setattr("inventory_service.db.get_db", lambda: tmp_db)

    db = init_inventory(seed=123)

    data = db.all()

    assert len(data) == 10
    for cat in data:
        m = CategoryWithItems(**cat)
        assert len(m.items) == 5
