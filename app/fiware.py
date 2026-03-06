from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


@dataclass
class OrionClient:
    base_url: str
    timeout: float
    fiware_service: str
    fiware_servicepath: str

    def _headers(self, include_content_type: bool = False) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if include_content_type:
            headers["Content-Type"] = "application/json"
        if self.fiware_service:
            headers["Fiware-Service"] = self.fiware_service
        if self.fiware_servicepath and self.fiware_service:
            headers["Fiware-ServicePath"] = self.fiware_servicepath
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        include_content_type = "json" in kwargs or "data" in kwargs
        headers = kwargs.pop("headers", {})
        merged_headers = {**self._headers(include_content_type=include_content_type), **headers}
        response = requests.request(
            method=method,
            url=f"{self.base_url}{path}",
            headers=merged_headers,
            timeout=self.timeout,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def list_entities(self, entity_type: str) -> List[Dict[str, Any]]:
        response = self._request(
            "GET",
            "/v2/entities",
            params={"type": entity_type, "options": "keyValues", "limit": 1000},
        )
        return response.json()

    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        response = self._request(
            "GET",
            f"/v2/entities/{entity_id}",
            params={"options": "keyValues"},
        )
        return response.json()

    def upsert_entity(self, entity: Dict[str, Any]) -> None:
        payload = {"actionType": "APPEND", "entities": [entity]}
        self._request("POST", "/v2/op/update", json=payload)

    def update_attrs(self, entity_id: str, attrs: Dict[str, Any]) -> None:
        self._request("PATCH", f"/v2/entities/{entity_id}/attrs", json=attrs)

    def delete_entity(self, entity_id: str) -> None:
        self._request("DELETE", f"/v2/entities/{entity_id}")

    def list_subscriptions(self) -> List[Dict[str, Any]]:
        response = self._request("GET", "/v2/subscriptions", params={"limit": 1000})
        return response.json()

    def create_subscription(self, payload: Dict[str, Any]) -> None:
        self._request("POST", "/v2/subscriptions", json=payload)

    def list_registrations(self) -> List[Dict[str, Any]]:
        response = self._request("GET", "/v2/registrations", params={"limit": 1000})
        return response.json()

    def create_registration(self, payload: Dict[str, Any]) -> None:
        self._request("POST", "/v2/registrations", json=payload)

    def delete_registration(self, registration_id: str) -> None:
        self._request("DELETE", f"/v2/registrations/{registration_id}")


ENTITY_PREFIXES = {
    "Store": "urn:ngsi-ld:Store",
    "Product": "urn:ngsi-ld:Product",
    "Shelf": "urn:ngsi-ld:Shelf",
    "InventoryItem": "urn:ngsi-ld:InventoryItem",
    "Employee": "urn:ngsi-ld:Employee",
}

STORE_CODES = ("001", "002", "003", "004")


def ensure_external_providers(client: OrionClient, provider_url: str) -> None:
    registrations = client.list_registrations()
    by_desc = {reg.get("description"): reg for reg in registrations}

    desired: List[Dict[str, Any]] = []
    for code in STORE_CODES:
        store_id = f"urn:ngsi-ld:Store:{code}"
        desired.append(
            {
                "description": f"Store {code} weather provider",
                "dataProvided": {
                    "entities": [{"type": "Store", "id": store_id}],
                    "attrs": ["temperature", "relativeHumidity"],
                },
                "provider": {
                    "http": {"url": f"{provider_url}/random/weatherConditions"},
                    "legacyForwarding": False,
                },
            }
        )
        desired.append(
            {
                "description": f"Store {code} tweets provider",
                "dataProvided": {
                    "entities": [{"type": "Store", "id": store_id}],
                    "attrs": ["tweets"],
                },
                "provider": {
                    "http": {"url": f"{provider_url}/catfacts/tweets"},
                    "legacyForwarding": False,
                },
            }
        )

    desired_by_desc = {item["description"]: item for item in desired}
    legacy_descriptions = {"Store weather provider", "Store tweets provider"}

    for description, current in by_desc.items():
        current_id = current.get("id")
        if not current_id:
            continue

        target = desired_by_desc.get(description)
        if target is None:
            if description in legacy_descriptions:
                client.delete_registration(current_id)
            continue

        current_data = current.get("dataProvided") or {}
        target_data = target.get("dataProvided") or {}
        current_url = (((current.get("provider") or {}).get("http") or {}).get("url"))
        target_url = (((target.get("provider") or {}).get("http") or {}).get("url"))

        if (
            current_url == target_url
            and current_data.get("entities") == target_data.get("entities")
            and current_data.get("attrs") == target_data.get("attrs")
        ):
            continue

        client.delete_registration(current_id)

    existing_descriptions = {
        reg.get("description")
        for reg in client.list_registrations()
    }

    for payload in desired:
        if payload["description"] not in existing_descriptions:
            client.create_registration(payload)


def _create_subscription_if_missing(client: OrionClient, description: str, payload: Dict[str, Any]) -> None:
    for subscription in client.list_subscriptions():
        if subscription.get("description") == description:
            return
    client.create_subscription(payload)


def ensure_subscriptions(client: OrionClient, app_base_url: str) -> None:
    _create_subscription_if_missing(
        client,
        "Product price change",
        {
            "description": "Product price change",
            "subject": {
                "entities": [{"type": "Product", "idPattern": ".*"}],
                "condition": {"attrs": ["price"]},
            },
            "notification": {
                "http": {"url": f"{app_base_url}/subscription/price-change"},
                "attrs": ["id", "name", "price"],
            },
            "throttling": 1,
        },
    )

    for code in ("001", "002", "003", "004"):
        _create_subscription_if_missing(
            client,
            f"Low stock store {code}",
            {
                "description": f"Low stock store {code}",
                "subject": {
                    "entities": [{"type": "InventoryItem", "idPattern": ".*"}],
                    "condition": {"attrs": ["shelfCount"], "expression": {"q": f"shelfCount<10;refStore==urn:ngsi-ld:Store:{code}"}},
                },
                "notification": {
                    "http": {"url": f"{app_base_url}/subscription/low-stock-store{code}"},
                    "attrs": ["id", "refStore", "refShelf", "refProduct", "shelfCount", "stockCount"],
                },
                "throttling": 1,
            },
        )


def make_id(entity_type: str, existing_ids: List[str]) -> str:
    prefix = ENTITY_PREFIXES[entity_type]
    max_idx = 0
    for value in existing_ids:
        if not value.startswith(prefix + ":"):
            continue
        try:
            max_idx = max(max_idx, int(value.rsplit(":", 1)[-1]))
        except ValueError:
            continue
    return f"{prefix}:{max_idx + 1:03d}"


def ngsi_attr(value: Any, attr_type: str) -> Dict[str, Any]:
    return {"type": attr_type, "value": value}


def to_product_entity(payload: Dict[str, Any], entity_id: str) -> Dict[str, Any]:
    return {
        "id": entity_id,
        "type": "Product",
        "name": ngsi_attr(payload["name"], "Text"),
        "price": ngsi_attr(float(payload["price"]), "Number"),
        "size": ngsi_attr(payload["size"], "Text"),
        "color": ngsi_attr(payload["color"], "Text"),
        "image": ngsi_attr(payload.get("image"), "Text"),
    }


def to_store_entity(payload: Dict[str, Any], entity_id: str) -> Dict[str, Any]:
    return {
        "id": entity_id,
        "type": "Store",
        "name": ngsi_attr(payload["name"], "Text"),
        "address": ngsi_attr(
            {
                "streetAddress": payload["streetAddress"],
                "addressRegion": payload["addressRegion"],
                "addressLocality": payload["addressLocality"],
                "postalCode": payload["postalCode"],
            },
            "PostalAddress",
        ),
        "location": ngsi_attr(
            {"type": "Point", "coordinates": [float(payload["longitude"]), float(payload["latitude"]) ]},
            "geo:json",
        ),
        "url": ngsi_attr(payload["url"], "Text"),
        "telephone": ngsi_attr(payload["telephone"], "Text"),
        "countryCode": ngsi_attr(payload["countryCode"], "Text"),
        "capacity": ngsi_attr(float(payload["capacity"]), "Number"),
        "description": ngsi_attr(payload["description"], "Text"),
        "image": ngsi_attr(payload.get("image"), "Text"),
    }


def to_employee_entity(payload: Dict[str, Any], entity_id: str) -> Dict[str, Any]:
    skills = [skill.strip() for skill in payload.get("skills", "").split(",") if skill.strip()]
    return {
        "id": entity_id,
        "type": "Employee",
        "name": ngsi_attr(payload["name"], "Text"),
        "image": ngsi_attr(payload["image"], "Text"),
        "salary": ngsi_attr(float(payload["salary"]), "Number"),
        "role": ngsi_attr(payload["role"], "Text"),
        "refStore": ngsi_attr(payload["refStore"], "Relationship"),
        "email": ngsi_attr(payload["email"], "Text"),
        "dateOfContract": ngsi_attr(payload["dateOfContract"], "Date"),
        "skills": ngsi_attr(skills, "StructuredValue"),
        "username": ngsi_attr(payload["username"], "Text"),
        "password": ngsi_attr(payload["password"], "Text"),
    }


def to_shelf_entity(payload: Dict[str, Any], entity_id: str) -> Dict[str, Any]:
    return {
        "id": entity_id,
        "type": "Shelf",
        "name": ngsi_attr(payload["name"], "Text"),
        "location": ngsi_attr(
            {"type": "Point", "coordinates": [float(payload["longitude"]), float(payload["latitude"]) ]},
            "geo:json",
        ),
        "maxCapacity": ngsi_attr(int(payload["maxCapacity"]), "Integer"),
        "refStore": ngsi_attr(payload["refStore"], "Relationship"),
    }


def to_inventory_item_entity(payload: Dict[str, Any], entity_id: str) -> Dict[str, Any]:
    return {
        "id": entity_id,
        "type": "InventoryItem",
        "refProduct": ngsi_attr(payload["refProduct"], "Relationship"),
        "refStore": ngsi_attr(payload["refStore"], "Relationship"),
        "refShelf": ngsi_attr(payload["refShelf"], "Relationship"),
        "stockCount": ngsi_attr(int(payload["stockCount"]), "Integer"),
        "shelfCount": ngsi_attr(int(payload["shelfCount"]), "Integer"),
    }


def safe_get(entity: Dict[str, Any], key: str, default: Any = None) -> Any:
    return entity.get(key, default)
