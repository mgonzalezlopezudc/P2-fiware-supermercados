import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:1026")
    ORION_TIMEOUT = float(os.getenv("ORION_TIMEOUT", "8"))
    CONTEXT_PROVIDER_URL = os.getenv("CONTEXT_PROVIDER_URL", "http://tutorial:3000")
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://host.docker.internal:5000")
    FIWARE_SERVICE = os.getenv("FIWARE_SERVICE", "")
    FIWARE_SERVICEPATH = os.getenv("FIWARE_SERVICEPATH", "/")
    AUTO_BOOTSTRAP = os.getenv("AUTO_BOOTSTRAP", "true").lower() == "true"
