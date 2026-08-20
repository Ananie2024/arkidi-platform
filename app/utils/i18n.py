"""
Backend Internationalization (i18n) Helper
Translations for Canonical & Administrative messages in EN, FR, RW
"""
from typing import Dict
from app.core.middleware import current_language_ctx

# Dictionary of core system strings in EN, FR, RW
MESSAGES: Dict[str, Dict[str, str]] = {
    "welcome": {
        "en": "Welcome to Arkidi Platform",
        "fr": "Bienvenue sur la plateforme Arkidi",
        "rw": "Murakaza neza kuri Arkidi Platform",
    },
    "unauthorized": {
        "en": "Authentication required",
        "fr": "Authentification requise",
        "rw": "Kwinjira birakenewe",
    },
    "forbidden": {
        "en": "Access forbidden: insufficient ecclesiastical permissions",
        "fr": "Accès interdit : permissions ecclésiastiques insuffisantes",
        "rw": "Uburenganzira ntibuhagije",
    },
    "not_found": {
        "en": "Requested record was not found",
        "fr": "Le dossier demandé est introuvable",
        "rw": "Inyandiko mwasabye ntiyabonetse",
    },
    "sacrament_recorded": {
        "en": "Sacrament entry successfully registered in the canonical book",
        "fr": "Sacrement enregistré avec succès dans le registre canonique",
        "rw": "Isakaramentu ryanditswe neza mu gitabo cya kiliziya",
    },
}


def get_translation(key: str, default: str = "") -> str:
    """Retrieve translated message based on current request language context."""
    lang = current_language_ctx.get()
    return MESSAGES.get(key, {}).get(lang, MESSAGES.get(key, {}).get("en", default or key))


def t(key: str, default: str = "") -> str:
    """Short alias for get_translation."""
    return get_translation(key, default)
