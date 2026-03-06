# Product Requirements Document

## Product
FIWARE Supermarkets management web app using Orion NGSIv2 as business data source.

## Goals
- Manage `Store`, `Product`, `Shelf`, `InventoryItem`, `Employee` entities with CRUD and relationship workflows.
- Integrate Orion context providers for store external attributes (`temperature`, `relativeHumidity`, `tweets`) using explicit registrations per store (`001`, `002`, `003`, `004`) without wildcard `idPattern`.
- Receive Orion subscriptions and update UI in real time through Socket.IO.

## Users
- Store operations staff.
- Inventory managers.
- Supervisors tracking low stock alerts.

## Functional Scope
- Sticky navigation and pages: `Home`, `Products`, `Product detail`, `Stores`, `Store detail`, `Employees`, `Stores Map`.
- CRUD operations for `Product`, `Store`, `Employee`.
- Shelf and inventory management with dynamic filtered selects.
- Purchase action reducing `shelfCount` and `stockCount` with empty shelf protection.
- Real-time price and low-stock notifications.
- `Stores Map` is implemented with Leaflet + OpenStreetMap tiles, with one marker per store based on NGSI `Store.location` coordinates.
- Leaflet map popups include store name, locality, and direct link to the store detail page.
- Store markers use a custom branded visual style to improve map readability.
- Map initialization includes CDN fallback loading to improve reliability when a provider is unavailable.
- Store detail shows compact temperature/humidity cards and a full-width tweets section to improve readability.
- Tweets layout in store detail is responsive: 3 columns on desktop, 2 on tablet, 1 on mobile.
- Bootstrap script `import-data` must seed all mandatory attributes defined in the data model for each entity type, except provider-managed `Store` attributes (`temperature`, `relativeHumidity`, `tweets`) which are supplied by registered Orion context providers.
- Seed dataset includes 4 employees and free-to-use, context-appropriate images for stores, products, and employees.

## Non-functional Requirements
- Flask + Jinja2 + plain HTML/CSS/JS.
- Orion NGSIv2 APIs for all entity persistence.
- Visual effects mostly done in CSS.
- Infrastructure lifecycle via `./services start` and `./services stop`.
