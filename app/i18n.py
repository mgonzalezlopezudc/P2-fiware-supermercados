from __future__ import annotations

from flask import current_app, request, session


def _supported_languages() -> list[str]:
    return current_app.config.get("LANGUAGES", ["es", "en"])


def resolve_locale() -> str:
    """Resolve the active locale with explicit user preference first."""
    supported = _supported_languages()

    requested = request.args.get("lang", "").strip().lower()
    if requested in supported:
        session["lang"] = requested
        return requested

    session_lang = (session.get("lang") or "").strip().lower()
    if session_lang in supported:
        return session_lang

    cookie_lang = (request.cookies.get("lang") or "").strip().lower()
    if cookie_lang in supported:
        return cookie_lang

    best = request.accept_languages.best_match(supported)
    if best:
        return best

    return current_app.config.get("BABEL_DEFAULT_LOCALE", "es")
