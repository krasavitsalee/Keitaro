import json


def test_index_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Keitaro Wrapper" in r.text


def test_creator_page(client):
    r = client.get("/creator")
    assert r.status_code == 200
    assert "Создаватор" in r.text


def test_editor_page(client):
    r = client.get("/editor")
    assert r.status_code == 200
    assert "Редактор" in r.text


def test_api_domains(client, mock_keitaro):
    r = client.get("/api/keitaro/domains")
    assert r.status_code == 200
    assert r.json()[0]["id"] == 1


def test_api_groups(client, mock_keitaro):
    r = client.get("/api/keitaro/groups")
    assert r.status_code == 200
    assert r.json()[0]["id"] == 2


def test_api_sources(client, mock_keitaro):
    r = client.get("/api/keitaro/sources")
    assert r.status_code == 200
    assert r.json()[0]["id"] == 3


def test_api_offers(client, mock_keitaro):
    r = client.get("/api/keitaro/offers")
    assert r.status_code == 200
    assert r.json()[0]["id"] == 10


def test_creator_create(client, mock_keitaro):
    body = {
        "name": "test_check",
        "country_code": "de",
        "offer_id": 10,
        "domain_id": 1,
        "group_id": 2,
        "traffic_source_id": 3,
    }
    r = client.post("/api/creator/create", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["campaign"]["id"] == 999
    # two streams created
    assert mock_keitaro.create_stream.call_count == 2


def test_editor_add_offer(client, mock_keitaro):
    # make stream have no offers initially for add test
    mock_keitaro.get_stream.return_value = {
        "id": 5, "campaign_id": 999, "type": "regular", "name": "Offer",
        "action_type": "http", "schema": "landings", "state": "active",
        "position": 2, "weight": 0, "collect_clicks": True, "filter_or": False,
        "filters": [], "landings": [], "offers": [],
    }
    r = client.post("/api/editor/streams/5/offers/add", json={"offer_id": 10})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_editor_remove_offer(client, mock_keitaro):
    r = client.post("/api/editor/streams/5/offers/remove", json={"offer_id": 10})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_creator_duplicate_name(client, mock_keitaro):
    mock_keitaro.list_campaigns.return_value = [{"id": 1, "name": "dup_name", "state": "active"}]
    body = {
        "name": "dup_name",
        "country_code": "de",
        "offer_id": 10,
        "domain_id": 1,
        "group_id": 2,
        "traffic_source_id": 3,
    }
    r = client.post("/api/creator/create", json=body)
    assert r.status_code == 400
    assert "не может повторяться" in r.json()["detail"]