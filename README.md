# FIWARE Supermarkets

Flask web application for supermarket management using FIWARE Orion (NGSIv2) as the system of record.

## What the app does
- Manages `Store`, `Product`, `Shelf`, `InventoryItem`, and `Employee` entities stored in Orion.
- Provides CRUD for `Store`, `Product`, and `Employee`.
- Supports shelf and inventory assignment from product/store detail screens.
- Executes purchase operations that decrement both `shelfCount` and `stockCount`.
- Receives Orion subscription notifications and pushes real-time updates with Flask-SocketIO.
- Displays stores on an interactive Leaflet/OpenStreetMap map.

## Quick start
1. Start infrastructure and seed data:
```bash
./services start
```
2. Install app dependencies:
```bash
pip install -r requirements.txt
```
3. Run the Flask app:
```bash
python run.py
```
4. Open:
- App: `http://localhost:5000`
- Orion monitor: `http://localhost:3000/app/monitor`

Stop infrastructure:
```bash
./services stop
```

## Runtime configuration

Environment variables loaded by `app/config.py`:

- `SECRET_KEY` (default `dev-secret-key`)
- `ORION_BASE_URL` (default `http://localhost:1026`)
- `ORION_TIMEOUT` (default `8` seconds)
- `CONTEXT_PROVIDER_URL` (default `http://context-provider:3000`)
- `APP_BASE_URL` (default `http://host.docker.internal:5000`)
- `FIWARE_SERVICE` (default empty)
- `FIWARE_SERVICEPATH` (default `/`)
- `AUTO_BOOTSTRAP` (default `true`)
- `SOCKETIO_ASYNC_MODE` (default `threading`)

## Startup bootstrap behavior

When `AUTO_BOOTSTRAP=true`, app startup:

- Reconciles Orion external provider registrations for stores `001` to `004`:
- Weather attrs: `temperature`, `relativeHumidity`
- Tweets attr: `tweets`
- Ensures subscriptions exist for:
- Product price changes (`/subscription/price-change`)
- Low stock (`shelfCount < 10`) for stores `001`, `002`, `003`, `004`

## Real-time behavior

- Orion notifications hit Flask endpoints under `/subscription/*`.
- Payloads are normalized to plain key-value JSON and emitted through Socket.IO.
- Browser listens for:
- `price_change`
- `low_stock_001`, `low_stock_002`, `low_stock_003`, `low_stock_004`
- UI updates prices and shows global toast notifications.

## Main routes

- UI pages: `/`, `/products`, `/products/<id>`, `/stores`, `/stores/<id>`, `/employees`, `/stores-map`
- CRUD/form actions: `/products/*`, `/stores/*`, `/employees/*`, `/shelves/*`, `/inventory/*`
- Dynamic select APIs:
- `/api/stores/<store_id>/available-shelves`
- `/api/shelves/<shelf_id>/available-products`
- Orion notification endpoints:
- `/subscription/price-change`
- `/subscription/low-stock-store001`
- `/subscription/low-stock-store002`
- `/subscription/low-stock-store003`
- `/subscription/low-stock-store004`

## Notes

- Orion remains the source of truth for all business entities.
- `SOCKETIO_ASYNC_MODE=eventlet` should only be used under an eventlet server runtime.
- If launched via `flask run`, configured `eventlet` mode is auto-adjusted to `threading` for compatibility.
