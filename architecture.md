# Architecture

## Runtime Components
- `Flask app` (`run.py`, `app/`): web UI, business workflows and Orion integration.
- `Flask-SocketIO`: server-side event hub for browser updates.
- `Orion Context Broker` (NGSIv2): source of truth for entities and subscriptions.
- `Tutorial context provider`: external provider for weather and tweets attributes.
- `Leaflet + OpenStreetMap`: client-side interactive map rendering for stores geolocation page.
- `MongoDB`: Orion persistence.

## Flow
1. App startup creates Orion client from environment variables.
2. App bootstraps provider registrations and mandatory subscriptions.
3. Provider bootstrap reconciles 8 registrations (weather and tweets for stores `001`-`004`) using exact `Store` IDs, and removes legacy wildcard registrations if present.
4. UI requests call Flask routes.
5. Flask routes read/write entities in Orion (`/v2/entities`, `/v2/op/update`, `/v2/entities/<id>/attrs`).
6. Orion posts notifications to Flask subscription endpoints.
7. Flask normalizes Orion notification entities to key-value payloads and emits Socket.IO events.
8. Browser consumes Socket.IO events using standard transport negotiation (websocket when available, polling fallback).
9. Frontend renders global toast notifications for incoming real-time events in any page/tab and updates page-specific widgets when applicable.
10. Browser loads Socket.IO client (`4.8.1`) from CDN with a valid SRI hash; if this check fails, no real-time event channel is established.
11. Store detail UI renders weather signals as compact metrics and displays tweets in a full-width panel with responsive 3/2/1 column layout.
12. Stores map UI renders Leaflet tiles and custom styled markers from server-provided `Store` entities (`location.coordinates`), auto-fitting bounds when multiple stores exist.
13. If Leaflet is unavailable from the primary CDN, the frontend retries loading from a secondary CDN before showing a map load error message.

## Main Files
- `app/fiware.py`: Orion client, NGSI serialization, startup bootstrap.
- `app/routes.py`: page routes, CRUD handlers, inventory operations, subscription endpoints.
- `app/templates/`: Jinja templates.
- `app/static/js/main.js`: Socket.IO, dynamic selects and Leaflet map initialization.
- `app/static/css/styles.css`: visual language, transitions, layout.

## Deployment Notes
- Start dependencies with `./services start`.
- Run app with `python run.py` (port `5000`).
- Default Socket.IO async mode is `threading` (compatible with Werkzeug/development runtime).
- Use `SOCKETIO_ASYNC_MODE=eventlet` only when deploying with an eventlet server runtime.
- When launched via Flask CLI (`flask run`), the app guards against invalid eventlet usage by forcing `threading` mode.
- Stop dependencies with `./services stop`.
- Load baseline entities with `./import-data` after Orion is up.

## Seed Data Conventions
- The `import-data` script seeds complete entity payloads with mandatory attributes required by `data_model.md`, except provider-managed `Store` attributes (`temperature`, `relativeHumidity`, `tweets`).
- Seed data includes 4 employees and free-to-use image URLs for entity types rendered with thumbnails in the UI.
