import os

from flask import Flask
from flask_babel import Babel, get_locale, gettext
from flask_socketio import SocketIO

from app.config import Config
from app.fiware import OrionClient, ensure_external_providers, ensure_subscriptions
from app.i18n import resolve_locale

socketio = SocketIO(cors_allowed_origins="*")
babel = Babel()


def _resolve_socketio_async_mode(configured_mode: str) -> str:
    mode = (configured_mode or "").strip().lower()
    supported_modes = {"threading", "eventlet", "gevent", "gevent_uwsgi"}
    if mode not in supported_modes:
        return "threading"

    # `flask run` uses Werkzeug and cannot serve eventlet websocket upgrades.
    if mode == "eventlet" and os.getenv("FLASK_RUN_FROM_CLI"):
        return "threading"

    return mode


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    babel.init_app(app, locale_selector=resolve_locale)

    @app.context_processor
    def inject_i18n_context() -> dict[str, object]:
        locale_code = str(get_locale())
        return {
            "current_locale": locale_code,
            "supported_locales": app.config["LANGUAGES"],
            "js_i18n": {
                "realtime_connection_issue": gettext("Realtime connection issue detected"),
                "price_updated": gettext(
                    "Price updated: product {product_id} now {price}"
                ),
                "low_stock": gettext(
                    "Low stock in store {store_code}: product {product_label} on shelf {shelf_label} (count={count})"
                ),
                "low_stock_panel": gettext(
                    "Low stock: {product} on {shelf} (shelfCount={count})"
                ),
                "no_available_shelf": gettext("No available shelf"),
                "no_available_product": gettext("No available product"),
                "unknown": gettext("unknown"),
                "store_fallback": gettext("Store"),
                "view_details": gettext("View details"),
                "map_payload_parse_error": gettext("Cannot parse stores map payload"),
                "map_load_error": gettext(
                    "Map cannot be loaded right now. Please check your network and reload the page."
                ),
            },
        }

    client = OrionClient(
        base_url=app.config["ORION_BASE_URL"],
        timeout=app.config["ORION_TIMEOUT"],
        fiware_service=app.config["FIWARE_SERVICE"],
        fiware_servicepath=app.config["FIWARE_SERVICEPATH"],
    )
    app.extensions["orion_client"] = client

    if app.config["AUTO_BOOTSTRAP"]:
        try:
            ensure_external_providers(client, app.config["CONTEXT_PROVIDER_URL"])
            ensure_subscriptions(client, app.config["APP_BASE_URL"])
        except Exception as error:  # pragma: no cover
            app.logger.warning("Bootstrap warning: %s", error)

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    configured_mode = app.config["SOCKETIO_ASYNC_MODE"]
    resolved_mode = _resolve_socketio_async_mode(configured_mode)
    if resolved_mode != (configured_mode or "").strip().lower():
        app.logger.warning(
            "Socket.IO async mode '%s' adjusted to '%s' for current runtime",
            configured_mode,
            resolved_mode,
        )

    socketio.init_app(app, async_mode=resolved_mode)
    return app
