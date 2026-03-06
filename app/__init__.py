from flask import Flask
from flask_socketio import SocketIO

from app.config import Config
from app.fiware import OrionClient, ensure_external_providers, ensure_subscriptions

socketio = SocketIO(async_mode="eventlet", cors_allowed_origins="*")


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

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
    socketio.init_app(app)
    return app
