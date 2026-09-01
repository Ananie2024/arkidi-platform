"""
Backend Internationalization (i18n) Service.

Loads message catalogs from ``app/locales/{en,fr,rw}/messages.json`` and
resolves translations for the active request language. The active language is
set per-request by :class:`app.core.middleware.LanguageMiddleware` through the
``current_language_ctx`` context variable, so every message returned by the API
("welcome", success, or error) respects the client's ``Accept-Language``.

Keys use dot notation, e.g. ``"errors.invalid_credentials"``. Placeholders use
the ``{{name}}`` syntax (mirroring i18next), for example::

    translate("errors.entity_not_found", {"entity": "Parish", "identifier": id})
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.middleware import current_language_ctx

# ---------------------------------------------------------------------------
# Layout / defaults
# ---------------------------------------------------------------------------
# app/locales/<lang>/messages.json
_LOCALES_DIR: Path = Path(__file__).resolve().parent.parent / "locales"
_MESSAGE_FILENAMES = ("messages.json", "errors.json", "common.json")
_FALLBACK_LANG: str = "en"
_SUPPORTED_LANGS: tuple[str, ...] = ("en", "fr", "rw")
_CATALOG_NAMESPACES: tuple[str, ...] = ("messages", "errors", "success", "common")


# ---------------------------------------------------------------------------
# Catalog loading & lookup
# ---------------------------------------------------------------------------
@lru_cache(maxsize=32)
def _load_catalog(lang: str) -> Dict[str, Any]:
    """Load and cache a locale catalog, merging every ``app/locales/<lang>/*.json`` file.

    Multiple files per language are supported so error catalogs can grow
    independently from success/common messages; files are merged in order.
    """
    catalog: Dict[str, Any] = {}
    lang_dir = _LOCALES_DIR / lang
    for filename in _MESSAGE_FILENAMES:
        path = lang_dir / filename
        if not path.is_file():
            continue
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                catalog.update(data)
        except (OSError, json.JSONDecodeError) as exc:  # pragma: no cover
            raise RuntimeError(f"Invalid i18n catalog at {path}: {exc}") from exc
    return catalog


def _resolve(catalog: Dict[str, Any], key: str) -> Optional[str]:
    """Dot-path lookup into a nested catalog (``"errors.parish_not_found"``)."""
    node: Any = catalog
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def _interpolate(template: str, params: Optional[Dict[str, Any]]) -> str:
    """Replace ``{{name}}`` placeholders with the given parameter values."""
    if not params:
        return template
    for name, value in params.items():
        template = template.replace("{{" + name + "}}", str(value))
    return template


def is_translation_key(value: Any) -> bool:
    """Return True when a string references a catalog key rather than literal text.

    Catalog keys always carry a dotted namespace (``errors.…``, ``success.…``);
    free-form messages (e.g. ``"Survey not found."``) can never be confused.
    """
    return (
        isinstance(value, str)
        and value.count(".") >= 1
        and value.split(".", 1)[0] in _CATALOG_NAMESPACES
    )


def get_translation(
    key: str,
    params: Optional[Dict[str, Any]] = None,
    default: str = "",
    lang: Optional[str] = None,
) -> str:
    """Translate ``key`` for the given/current request language.

    Falls back to the default language catalog, and finally to ``default`` (or
    the key itself) when the key cannot be resolved anywhere.
    """
    if lang is None:
        lang = current_language_ctx.get()
    if lang not in _SUPPORTED_LANGS:
        lang = _FALLBACK_LANG

    template = _resolve(_load_catalog(lang), key)
    if template is None and lang != _FALLBACK_LANG:
        template = _resolve(_load_catalog(_FALLBACK_LANG), key)
    if template is None:
        return default or key
    return _interpolate(template, params)


def t(
    key: str,
    params: Optional[Dict[str, Any]] = None,
    default: str = "",
    lang: Optional[str] = None,
) -> str:
    """Short alias for :func:`get_translation`."""
    return get_translation(key, params=params, default=default, lang=lang)
