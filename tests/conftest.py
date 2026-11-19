import os
# Set env before importing app
os.environ.setdefault("KEITARO_URL", "https://example.com")
os.environ.setdefault("KEITARO_API_KEY", "test-key")
import tempfile
_db_path = os.path.join(tempfile.gettempdir(), "test_keitaro_wrapper.db")
if os.path.exists(_db_path):
    os.remove(_db_path)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_db_path}")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_keitaro(monkeypatch):
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.list_domains.return_value = [{"id": 1, "name": "d.com", "state": "active"}]
    mock.list_groups.return_value = [{"id": 2, "name": "g", "type": "campaigns"}]
    mock.list_traffic_sources.return_value = [{"id": 3, "name": "src", "state": "active"}]
    mock.list_offers.return_value = [{"id": 10, "name": "offer", "state": "active"}]
    mock.ensure_domain.return_value = 1
    mock.ensure_group.return_value = 2
    mock.ensure_traffic_source.return_value = 3
    mock.pick_redirect_action.return_value = "http"
    mock.pick_landing_action.return_value = "http"
    mock.create_campaign.return_value = {"id": 999, "name": "test", "alias": "a"}
    mock.create_stream.return_value = {"id": 1, "offers": []}
    mock.get_stream.return_value = {
        "id": 5, "campaign_id": 999, "type": "regular", "name": "Offer",
        "action_type": "http", "schema": "landings", "state": "active",
        "position": 2, "weight": 0, "collect_clicks": True, "filter_or": False,
        "filters": [], "landings": [], "offers": [{"offer_id": 10, "share": 100, "state": "active"}],
    }
    mock.update_stream.return_value = {"id": 5, "offers": []}
    mock.list_campaigns.return_value = [{"id": 999, "name": "test_camp", "state": "active"}]
    mock.list_streams.return_value = [{"id": 5, "name": "Offer", "state": "active", "offers": [{"offer_id": 10, "share": 100}]}]

    # patch in both routers
    monkeypatch.setattr("app.routers.creator.KeitaroClient", lambda *a, **k: mock)
    monkeypatch.setattr("app.routers.editor.KeitaroClient", lambda *a, **k: mock)
    return mock