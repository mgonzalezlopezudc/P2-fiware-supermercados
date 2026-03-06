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
7. Flask emits Socket.IO events, browser updates relevant widgets/tables without page refresh.
8. Store detail UI renders weather signals as compact metrics and displays tweets in a full-width panel with responsive 3/2/1 column layout.
9. Stores map UI renders Leaflet tiles and custom styled markers from server-provided `Store` entities (`location.coordinates`), auto-fitting bounds when multiple stores exist.
10. If Leaflet is unavailable from the primary CDN, the frontend retries loading from a secondary CDN before showing a map load error message.

## Main Files
- `app/fiware.py`: Orion client, NGSI serialization, startup bootstrap.
- `app/routes.py`: page routes, CRUD handlers, inventory operations, subscription endpoints.
- `app/templates/`: Jinja templates.
- `app/static/js/main.js`: Socket.IO, dynamic selects and Leaflet map initialization.
- `app/static/css/styles.css`: visual language, transitions, layout.

## Deployment Notes
- Start dependencies with `./services start`.
- Run app with `python run.py` (port `5000`).
- Stop dependencies with `./services stop`.
- Load baseline entities with `./import-data` after Orion is up.

## Seed Data Conventions
- The `import-data` script seeds complete entity payloads with mandatory attributes required by `data_model.md`, except provider-managed `Store` attributes (`temperature`, `relativeHumidity`, `tweets`).
- Seed data includes 4 employees and free-to-use image URLs for entity types rendered with thumbnails in the UI.
