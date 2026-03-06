# Architecture

## Runtime Components
- `Flask app` (`run.py`, `app/`): web UI, business workflows and Orion integration.
- `Flask-SocketIO`: server-side event hub for browser updates.
- `Orion Context Broker` (NGSIv2): source of truth for entities and subscriptions.
- `Tutorial context provider`: external provider for weather and tweets attributes.
- `MongoDB`: Orion persistence.

## Flow
1. App startup creates Orion client from environment variables.
2. App bootstraps provider registrations and mandatory subscriptions.
3. UI requests call Flask routes.
4. Flask routes read/write entities in Orion (`/v2/entities`, `/v2/op/update`, `/v2/entities/<id>/attrs`).
5. Orion posts notifications to Flask subscription endpoints.
6. Flask emits Socket.IO events, browser updates relevant widgets/tables without page refresh.

## Main Files
- `app/fiware.py`: Orion client, NGSI serialization, startup bootstrap.
- `app/routes.py`: page routes, CRUD handlers, inventory operations, subscription endpoints.
- `app/templates/`: Jinja templates.
- `app/static/js/main.js`: Socket.IO and dynamic select behavior.
- `app/static/css/styles.css`: visual language, transitions, layout.

## Deployment Notes
- Start dependencies with `./services start`.
- Run app with `python run.py` (port `5000`).
- Stop dependencies with `./services stop`.
