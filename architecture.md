# Architecture

## Runtime components
- `run.py` and `app/__init__.py`: Flask app factory and Socket.IO initialization.
- `app/i18n.py`: locale resolution (`?lang` -> session -> cookie -> `Accept-Language` -> default).
- `app/fiware.py`: Orion client wrapper, ID generation, entity serializers, bootstrap logic.
- `app/routes.py`: UI handlers, CRUD actions, inventory workflows, REST helper APIs, and subscription callbacks.
- `app/templates/*`: server-rendered Jinja pages and forms.
- `app/static/js/main.js`: real-time listeners, toasts, dynamic selects, map loader.
- `app/static/css/styles.css`: layout, responsive behavior, map/notification styles.
- `translations/*/LC_MESSAGES/messages.po|messages.mo`: gettext catalogs used by Flask-Babel.
- `docker-compose.yml`: Orion, tutorial context provider, and MongoDB services.
- `services` and `import-data`: infra lifecycle helper and seed loading.

## High-level flow
1. App startup loads config from environment (`app/config.py`).
2. `OrionClient` is created and stored in `app.extensions["orion_client"]`.
3. If `AUTO_BOOTSTRAP=true`, startup ensures:
	- External provider registrations for stores `001` to `004`.
	- Orion subscriptions for product price changes and low-stock events.
4. UI requests hit Flask routes that read/write Orion entities in key-values mode.
5. Orion sends subscription callbacks to `/subscription/*` endpoints.
6. Flask normalizes callback payloads and emits Socket.IO events.
7. Browser receives events, updates price cells, and displays global toasts.

## Orion integration details

### Entity operations
- List entities: `GET /v2/entities?type=<type>&options=keyValues`
- Read entity: `GET /v2/entities/<id>?options=keyValues`
- Upsert entity: `POST /v2/op/update` with `actionType=APPEND`
- Patch attrs: `PATCH /v2/entities/<id>/attrs`
- Delete entity: `DELETE /v2/entities/<id>`

### Bootstrapped registrations
- Exactly 8 registrations are maintained:
- `Store 00X weather provider`
- `Store 00X tweets provider`
- Scope is exact `Store` IDs (`urn:ngsi-ld:Store:001` to `004`).
- Legacy descriptions (`Store weather provider`, `Store tweets provider`) are removed if found.

### Bootstrapped subscriptions
- `Product price change`: monitors `Product.price`, notifies `/subscription/price-change`.
- `Low stock store 001..004`: monitors `InventoryItem.shelfCount` with expression:
- `shelfCount<10;refStore==urn:ngsi-ld:Store:<code>`
- Notify endpoints `/subscription/low-stock-store001..004`.

## Frontend behavior
- Socket.IO client from CDN (`4.8.1`) is loaded in `app/templates/base.html`.
- Events handled by `main.js`:
- `price_change` updates DOM prices (`.js-price`) and shows info toast.
- `low_stock_00X` shows warning toasts and appends rows to store notification panel when applicable.
- Leaflet map loader uses primary and fallback CDN script URLs.
- If Leaflet cannot be loaded, the map container shows a clear error message.

## Internationalization
- Localization engine: `Flask-Babel` initialized in `app/__init__.py`.
- Supported locales: `es`, `en`.
- Default locale: `es`.
- Locale selection flow:
- Explicit URL override with `?lang=<locale>`.
- Persisted preference in Flask session.
- Persisted preference in cookie (`lang`, 1 year).
- Browser negotiation via `Accept-Language`.
- Fallback to configured default locale.
- Language switching endpoint: `POST /set-language` with safe redirect validation.
- Templates use gettext helpers (`_`) for visible text and set `<html lang="{{ current_locale }}">`.
- JavaScript messages are translated server-side and injected as `window.I18N` in `base.html`.

## HTTP surface

### User-facing pages
- `/`
- `/products`, `/products/new`, `/products/<id>`, `/products/<id>/edit`, `/products/<id>/delete`
- `/stores`, `/stores/new`, `/stores/<id>`, `/stores/<id>/edit`, `/stores/<id>/delete`
- `/employees`, `/employees/new`, `/employees/<id>/edit`, `/employees/<id>/delete`
- `/stores-map`

### Operational endpoints
- `/shelves/new`, `/shelves/<id>/edit`
- `/inventory/new`, `/inventory/<id>/buy`
- `/api/stores/<store_id>/available-shelves`
- `/api/shelves/<shelf_id>/available-products`
- `/subscription/price-change`
- `/subscription/low-stock-store001`
- `/subscription/low-stock-store002`
- `/subscription/low-stock-store003`
- `/subscription/low-stock-store004`

## Deployment and runtime notes
- Infra is started/stopped through `./services start` and `./services stop`.
- App is launched with `python run.py` and binds `0.0.0.0:5000`.
- Default Socket.IO async mode is `threading`.
- If `SOCKETIO_ASYNC_MODE=eventlet` is set but app runs via Flask CLI, mode is auto-adjusted to `threading`.
