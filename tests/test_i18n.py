from __future__ import annotations

import pytest

from app import create_app


class FakeOrionClient:
    def __init__(self) -> None:
        self._entities = {
            "Store": [],
            "Product": [],
            "Shelf": [],
            "InventoryItem": [],
            "Employee": [],
        }

    def list_entities(self, entity_type: str):
        return list(self._entities.get(entity_type, []))

    def upsert_entity(self, entity):
        entity_type = entity.get("type")
        if entity_type in self._entities:
            values = {
                k: v.get("value")
                for k, v in entity.items()
                if isinstance(v, dict) and "value" in v
            }
            self._entities[entity_type].append({"id": entity["id"], **values})

    def get_entity(self, entity_id: str):
        return {"id": entity_id, "refStore": "urn:ngsi-ld:Store:001", "shelfCount": 3}

    def delete_entity(self, entity_id: str):
        return None

    def update_attrs(self, entity_id: str, attrs):
        return None


@pytest.fixture
def app_instance(monkeypatch):
    monkeypatch.setenv("AUTO_BOOTSTRAP", "false")
    app = create_app()
    app.config.update(TESTING=True)
    app.extensions["orion_client"] = FakeOrionClient()
    return app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


def test_default_locale_is_spanish(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'lang="es"' in html
    assert "Inicio" in html


def test_query_param_overrides_to_english(client):
    response = client.get("/?lang=en")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'lang="en"' in html
    assert "Home" in html


def test_language_switch_endpoint_persists_cookie(client):
    response = client.post(
        "/set-language",
        data={"lang": "en", "next": "/products"},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/products")
    assert "lang=en" in response.headers.get("Set-Cookie", "")


def test_flash_message_translates_in_spanish(client):
    with client.session_transaction() as sess:
        sess["lang"] = "es"

    response = client.post(
        "/products/new",
        data={
            "name": "Test product",
            "price": "10.50",
            "size": "M",
            "color": "#112233",
            "image": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Producto creado" in response.get_data(as_text=True)
