import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:1026")
    ORION_TIMEOUT = float(os.getenv("ORION_TIMEOUT", "8"))
    CONTEXT_PROVIDER_URL = os.getenv("CONTEXT_PROVIDER_URL", "http://context-provider:3000")
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://host.docker.internal:5000")
    FIWARE_SERVICE = os.getenv("FIWARE_SERVICE", "")
    FIWARE_SERVICEPATH = os.getenv("FIWARE_SERVICEPATH", "/")
    AUTO_BOOTSTRAP = os.getenv("AUTO_BOOTSTRAP", "true").lower() == "true"
    # Use a Werkzeug-compatible default in development. Set to "eventlet" for eventlet deployments.
    SOCKETIO_ASYNC_MODE = os.getenv("SOCKETIO_ASYNC_MODE", "threading")
    BABEL_DEFAULT_LOCALE = os.getenv("BABEL_DEFAULT_LOCALE", "es")
    BABEL_DEFAULT_TIMEZONE = os.getenv("BABEL_DEFAULT_TIMEZONE", "UTC")
    BABEL_TRANSLATION_DIRECTORIES = os.getenv(
        "BABEL_TRANSLATION_DIRECTORIES", os.path.join(BASE_DIR, "translations")
    )
    LANGUAGES = ["es", "en"]
