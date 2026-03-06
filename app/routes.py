from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from flask import Blueprint, Response, current_app, flash, jsonify, redirect, render_template, request, url_for

from app import socketio
from app.fiware import (
    OrionClient,
    make_id,
    to_employee_entity,
    to_inventory_item_entity,
    to_product_entity,
    to_shelf_entity,
    to_store_entity,
)

main_bp = Blueprint("main", __name__)


ROLE_COLORS = {
    "manager": "#d95f02",
    "cashier": "#1b9e77",
    "warehouse": "#7570b3",
    "security": "#e7298a",
    "cleaning": "#66a61e",
}


@main_bp.app_template_filter("role_color")
def role_color(role: str) -> str:
    return ROLE_COLORS.get((role or "").lower(), "#4e5d6c")


@main_bp.app_template_filter("short_id")
def short_id(value: str) -> str:
    return value.rsplit(":", 1)[-1] if value else ""


def get_client() -> OrionClient:
    return current_app.extensions["orion_client"]


def load_all() -> Dict[str, List[Dict[str, Any]]]:
    client = get_client()
    return {
        "stores": client.list_entities("Store"),
        "products": client.list_entities("Product"),
        "shelves": client.list_entities("Shelf"),
        "inventory": client.list_entities("InventoryItem"),
        "employees": client.list_entities("Employee"),
    }


@main_bp.route("/")
def home():
    data = load_all()
    metrics = {
        "stores": len(data["stores"]),
        "products": len(data["products"]),
        "shelves": len(data["shelves"]),
        "inventory": len(data["inventory"]),
        "employees": len(data["employees"]),
    }
    return render_template("pages/home.html", active="home", metrics=metrics)


@main_bp.route("/products")
def products():
    data = load_all()
    return render_template("pages/products.html", active="products", products=data["products"])


@main_bp.route("/products/new", methods=["GET", "POST"])
def product_new():
    client = get_client()
    if request.method == "POST":
        existing_ids = [entity["id"] for entity in client.list_entities("Product")]
        entity_id = make_id("Product", existing_ids)
        client.upsert_entity(to_product_entity(request.form, entity_id))
        flash("Product created", "success")
        return redirect(url_for("main.products"))
    return render_template("forms/product_form.html", active="products", product=None)


@main_bp.route("/products/<path:product_id>")
def product_detail(product_id: str):
    client = get_client()
    product = client.get_entity(product_id)
    stores = {s["id"]: s for s in client.list_entities("Store")}
    shelves = {s["id"]: s for s in client.list_entities("Shelf")}
    inventory = [item for item in client.list_entities("InventoryItem") if item.get("refProduct") == product_id]

    grouped: Dict[str, Dict[str, Any]] = {}
    for item in inventory:
        store_id = item.get("refStore")
        if not store_id:
            continue
        if store_id not in grouped:
            grouped[store_id] = {"store": stores.get(store_id), "total": 0, "items": []}
        grouped[store_id]["total"] += int(item.get("shelfCount", 0))
        grouped[store_id]["items"].append({"inventory": item, "shelf": shelves.get(item.get("refShelf"))})

    return render_template(
        "pages/product_detail.html",
        active="products",
        product=product,
        grouped=grouped,
        stores=stores,
        shelves=shelves,
    )


@main_bp.route("/products/<path:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id: str):
    client = get_client()
    if request.method == "POST":
        client.upsert_entity(to_product_entity(request.form, product_id))
        flash("Product updated", "success")
        return redirect(url_for("main.products"))
    product = client.get_entity(product_id)
    return render_template("forms/product_form.html", active="products", product=product)


@main_bp.route("/products/<path:product_id>/delete", methods=["POST"])
def product_delete(product_id: str):
    client = get_client()
    client.delete_entity(product_id)
    flash("Product deleted", "success")
    return redirect(url_for("main.products"))


@main_bp.route("/stores")
def stores():
    client = get_client()
    return render_template("pages/stores.html", active="stores", stores=client.list_entities("Store"))


@main_bp.route("/stores/new", methods=["GET", "POST"])
def store_new():
    client = get_client()
    if request.method == "POST":
        existing_ids = [entity["id"] for entity in client.list_entities("Store")]
        entity_id = make_id("Store", existing_ids)
        client.upsert_entity(to_store_entity(request.form, entity_id))
        flash("Store created", "success")
        return redirect(url_for("main.stores"))
    return render_template("forms/store_form.html", active="stores", store=None)


@main_bp.route("/stores/<path:store_id>")
def store_detail(store_id: str):
    client = get_client()
    store = client.get_entity(store_id)
    shelves = [s for s in client.list_entities("Shelf") if s.get("refStore") == store_id]
    products = {p["id"]: p for p in client.list_entities("Product")}
    inventory = [item for item in client.list_entities("InventoryItem") if item.get("refStore") == store_id]

    by_shelf: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for item in inventory:
        shelf_id = item.get("refShelf")
        if not shelf_id:
            continue
        by_shelf[shelf_id].append(item)

    shelf_rows = []
    for shelf in shelves:
        shelf_id = shelf["id"]
        shelf_items = by_shelf.get(shelf_id, [])
        current = sum(int(entry.get("shelfCount", 0)) for entry in shelf_items)
        max_capacity = int(shelf.get("maxCapacity", 1)) or 1
        percent = min(100, int((current / max_capacity) * 100))

        rows = []
        for inv in shelf_items:
            rows.append({"inventory": inv, "product": products.get(inv.get("refProduct"))})

        shelf_rows.append(
            {
                "shelf": shelf,
                "items": rows,
                "progress": percent,
                "current": current,
                "max": max_capacity,
            }
        )

    return render_template(
        "pages/store_detail.html",
        active="stores",
        store=store,
        shelf_rows=shelf_rows,
        products=products,
    )


@main_bp.route("/stores/<path:store_id>/edit", methods=["GET", "POST"])
def store_edit(store_id: str):
    client = get_client()
    if request.method == "POST":
        client.upsert_entity(to_store_entity(request.form, store_id))
        flash("Store updated", "success")
        return redirect(url_for("main.stores"))
    store = client.get_entity(store_id)
    return render_template("forms/store_form.html", active="stores", store=store)


@main_bp.route("/stores/<path:store_id>/delete", methods=["POST"])
def store_delete(store_id: str):
    client = get_client()
    client.delete_entity(store_id)
    flash("Store deleted", "success")
    return redirect(url_for("main.stores"))


@main_bp.route("/employees")
def employees():
    client = get_client()
    stores = {store["id"]: store for store in client.list_entities("Store")}
    return render_template(
        "pages/employees.html",
        active="employees",
        employees=client.list_entities("Employee"),
        stores=stores,
    )


@main_bp.route("/employees/new", methods=["GET", "POST"])
def employee_new():
    client = get_client()
    stores = client.list_entities("Store")
    if request.method == "POST":
        existing_ids = [entity["id"] for entity in client.list_entities("Employee")]
        entity_id = make_id("Employee", existing_ids)
        client.upsert_entity(to_employee_entity(request.form, entity_id))
        flash("Employee created", "success")
        return redirect(url_for("main.employees"))
    return render_template("forms/employee_form.html", active="employees", employee=None, stores=stores)


@main_bp.route("/employees/<path:employee_id>/edit", methods=["GET", "POST"])
def employee_edit(employee_id: str):
    client = get_client()
    stores = client.list_entities("Store")
    if request.method == "POST":
        client.upsert_entity(to_employee_entity(request.form, employee_id))
        flash("Employee updated", "success")
        return redirect(url_for("main.employees"))
    employee = client.get_entity(employee_id)
    return render_template("forms/employee_form.html", active="employees", employee=employee, stores=stores)


@main_bp.route("/employees/<path:employee_id>/delete", methods=["POST"])
def employee_delete(employee_id: str):
    client = get_client()
    client.delete_entity(employee_id)
    flash("Employee deleted", "success")
    return redirect(url_for("main.employees"))


@main_bp.route("/stores-map")
def stores_map():
    client = get_client()
    stores = client.list_entities("Store")
    return render_template("pages/stores_map.html", active="stores_map", stores=stores)


@main_bp.route("/shelves/new", methods=["POST"])
def shelf_new():
    client = get_client()
    existing_ids = [entity["id"] for entity in client.list_entities("Shelf")]
    entity_id = make_id("Shelf", existing_ids)
    client.upsert_entity(to_shelf_entity(request.form, entity_id))
    flash("Shelf created", "success")
    return redirect(url_for("main.store_detail", store_id=request.form["refStore"]))


@main_bp.route("/shelves/<path:shelf_id>/edit", methods=["POST"])
def shelf_edit(shelf_id: str):
    client = get_client()
    client.upsert_entity(to_shelf_entity(request.form, shelf_id))
    flash("Shelf updated", "success")
    return redirect(url_for("main.store_detail", store_id=request.form["refStore"]))


@main_bp.route("/inventory/new", methods=["POST"])
def inventory_new():
    client = get_client()
    existing_ids = [entity["id"] for entity in client.list_entities("InventoryItem")]
    entity_id = make_id("InventoryItem", existing_ids)
    client.upsert_entity(to_inventory_item_entity(request.form, entity_id))
    flash("Inventory item created", "success")

    redirect_to = request.form.get("redirectTo", "store")
    if redirect_to == "product":
        return redirect(url_for("main.product_detail", product_id=request.form["refProduct"]))
    return redirect(url_for("main.store_detail", store_id=request.form["refStore"]))


@main_bp.route("/inventory/<path:inventory_id>/buy", methods=["POST"])
def buy_inventory_item(inventory_id: str):
    client = get_client()
    item = client.get_entity(inventory_id)
    store_id = item.get("refStore")

    if int(item.get("shelfCount", 0)) <= 0:
        flash("Purchase blocked: shelf stock is empty", "error")
        return redirect(url_for("main.store_detail", store_id=store_id))

    client.update_attrs(
        inventory_id,
        {
            "shelfCount": {"type": "Integer", "value": {"$inc": -1}},
            "stockCount": {"type": "Integer", "value": {"$inc": -1}},
        },
    )
    flash("One unit purchased", "success")
    return redirect(url_for("main.store_detail", store_id=store_id))


@main_bp.route("/api/stores/<path:store_id>/available-shelves")
def api_available_shelves(store_id: str):
    client = get_client()
    product_id = request.args.get("product_id", "")
    shelves = [s for s in client.list_entities("Shelf") if s.get("refStore") == store_id]
    inventory = [
        item
        for item in client.list_entities("InventoryItem")
        if item.get("refStore") == store_id and item.get("refProduct") == product_id
    ]
    used = {item.get("refShelf") for item in inventory}
    available = [shelf for shelf in shelves if shelf.get("id") not in used]
    return jsonify(available)


@main_bp.route("/api/shelves/<path:shelf_id>/available-products")
def api_available_products(shelf_id: str):
    client = get_client()
    inventory = [item for item in client.list_entities("InventoryItem") if item.get("refShelf") == shelf_id]
    used = {item.get("refProduct") for item in inventory}
    products = [product for product in client.list_entities("Product") if product.get("id") not in used]
    return jsonify(products)


def _handle_notification(event_name: str, payload: Dict[str, Any]) -> Response:
    data = payload.get("data", [])
    current_app.logger.info("Subscription %s received %s items", event_name, len(data))
    socketio.emit(event_name, {"items": data})
    return Response(status=204)


@main_bp.route("/subscription/price-change", methods=["POST"])
def sub_price_change() -> Response:
    return _handle_notification("price_change", request.get_json(silent=True) or {})


@main_bp.route("/subscription/low-stock-store001", methods=["POST"])
def sub_low_stock_001() -> Response:
    return _handle_notification("low_stock_001", request.get_json(silent=True) or {})


@main_bp.route("/subscription/low-stock-store002", methods=["POST"])
def sub_low_stock_002() -> Response:
    return _handle_notification("low_stock_002", request.get_json(silent=True) or {})


@main_bp.route("/subscription/low-stock-store003", methods=["POST"])
def sub_low_stock_003() -> Response:
    return _handle_notification("low_stock_003", request.get_json(silent=True) or {})


@main_bp.route("/subscription/low-stock-store004", methods=["POST"])
def sub_low_stock_004() -> Response:
    return _handle_notification("low_stock_004", request.get_json(silent=True) or {})
