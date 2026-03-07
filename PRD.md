# Product Requirements Document

## Product
FIWARE Supermarkets is a Flask web UI over Orion NGSIv2 to manage supermarket entities and monitor real-time updates.

## Objectives
- Keep Orion as the single source of truth for supermarket business entities.
- Provide operational CRUD workflows for daily store management.
- Integrate external context-provider attributes for stores (`temperature`, `relativeHumidity`, `tweets`).
- Surface Orion subscription events to users in real time via Socket.IO.

## Users
- Store operations staff.
- Inventory managers.
- Supervisors monitoring low-stock conditions.

## Functional requirements

### Entity coverage
- Supported entity types: `Store`, `Product`, `Shelf`, `InventoryItem`, `Employee`.
- Full CRUD screens and handlers for `Store`, `Product`, `Employee`.
- `Shelf` and `InventoryItem` creation/edit flows embedded in detail pages.

### Navigation and views
- Top-level views: `Home`, `Products`, `Stores`, `Employees`, `Stores Map`.
- `Home` displays KPI counters and a Mermaid class diagram.
- `Product detail` groups inventory by store and allows adding inventory to unused shelves.
- `Store detail` groups inventory by shelf, shows shelf fill progress, and allows purchases.
- `Store detail` displays store weather metrics and tweets data when present.

### Multilanguage support
- UI supports `Spanish` and `English`.
- Default locale is `Spanish` when no preference is provided.
- Language can be switched from the navbar selector and persists in session/cookie.
- Locale resolution priority: query parameter (`?lang=`), session, cookie, `Accept-Language`, then default locale.
- All user-facing text in routes, templates, and frontend dynamic notifications is translatable.

### Business operations
- Purchase operation (`/inventory/<id>/buy`) must decrement:
- `shelfCount` by `-1`
- `stockCount` by `-1`
- Purchase is blocked when `shelfCount <= 0`.

### Dynamic validation and helpers
- HTML forms use built-in constraints (`required`, `min`, `pattern`, `type`, etc.).
- Frontend JS blocks invalid form submissions on `novalidate` forms.
- Dynamic select APIs prevent duplicate product/shelf assignments:
- Available shelves for a product in a store.
- Available products for a shelf.

### Real-time updates
- Startup ensures Orion subscriptions exist for:
- Product price changes.
- Low stock (`shelfCount < 10`) per store `001` to `004`.
- Notification endpoints receive Orion payloads, normalize values, and emit Socket.IO events.
- Frontend updates visible prices and shows global toast notifications.

### External provider integration
- Startup ensures exact-ID registrations for stores `001`, `002`, `003`, `004`.
- Provider-managed attributes:
- `temperature`, `relativeHumidity` from weather endpoint.
- `tweets` from tweets endpoint.

### Map experience
- `Stores Map` renders Leaflet markers from `Store.location.coordinates` (`[lon, lat]`).
- Popup content includes store name, optional locality, and a detail-page link.
- Leaflet script loading includes fallback CDN; if all loads fail, show a user-visible error message.

## Non-functional requirements
- Stack: Flask, Jinja2 templates, vanilla JavaScript/CSS, Flask-SocketIO.
- Data access: Orion NGSIv2 (`/v2/entities`, `/v2/op/update`, `/v2/entities/<id>/attrs`, subscriptions, registrations).
- Runtime compatibility: default Socket.IO async mode is `threading`; `eventlet` is supported only with eventlet runtime.
- Reliability safeguard: when started via `flask run`, configured `eventlet` mode is auto-adjusted to `threading`.
- Internationalization runtime uses `Flask-Babel` catalogs under `translations/`.
- Infrastructure lifecycle uses repository scripts (`./services start`, `./services stop`).
- Seed script (`import-data`) initializes baseline entities for all managed types, with provider-managed store attrs supplied by context providers.
