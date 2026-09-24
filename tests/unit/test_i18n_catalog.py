"""
Unit tests for the backend i18n message catalog and the LanguageMiddleware
integration through exception localization.
"""

import json
from pathlib import Path

import pytest

from app.core.exceptions import (
    DuplicateUPIException,
    EntityNotFoundException,
    InvalidCredentialsException,
    PermissionDeniedException,
)
from app.core.middleware import current_language_ctx
from app.utils.i18n import get_translation, is_translation_key
from app.utils.response import ApiResponse


class TestCatalogParity:
    """The en/fr/rw message catalogs must expose identical key sets so no
    language silently falls back for any message."""

    @pytest.mark.parametrize("other", ["fr", "rw"])
    def test_key_parity_with_english(self, other):
        base = self._flatten(self._load("en"))
        candidate = self._flatten(self._load(other))
        assert set(base) == set(candidate)

    def _load(self, lang: str):
        path = Path(__file__).resolve().parents[2] / "app" / "locales" / lang / "messages.json"
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _flatten(data, prefix=""):
        flat = {}
        for key, value in data.items():
            dotted = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flat.update(TestCatalogParity._flatten(value, dotted))
            else:
                flat[dotted] = value
        return flat


class TestTranslationService:
    def test_get_translation_english(self):
        assert (
            get_translation("errors.invalid_credentials", lang="en")
            == "Invalid username or password."
        )

    def test_get_translation_french(self):
        assert (
            get_translation("errors.invalid_credentials", lang="fr")
            == "Identifiant ou mot de passe invalide."
        )

    def test_get_translation_kinyarwanda(self):
        assert (
            get_translation("errors.invalid_credentials", lang="rw")
            == "Izina cyangwa ijambobanga ntibikwiye."
        )

    def test_unknown_language_falls_back_to_english(self):
        assert get_translation("welcome", lang="xx") == "Welcome to Arkidi Platform"

    def test_missing_key_returns_default(self):
        assert get_translation("errors.does_not_exist", default="fallback", lang="en") == "fallback"

    def test_missing_key_returns_key(self):
        assert get_translation("errors.does_not_exist", lang="en") == "errors.does_not_exist"

    def test_placeholder_interpolation(self):
        msg = get_translation(
            "errors.entity_not_found",
            {"entity": "Parish", "identifier": "p-1"},
            lang="fr",
        )
        assert msg == "Parish avec l'identifiant 'p-1' est introuvable."

    def test_is_translation_key(self):
        assert is_translation_key("errors.survey_not_found") is True
        assert is_translation_key("success.login_successful") is True
        assert is_translation_key("Survey not found.") is False

    def test_current_language_context(self):
        token = current_language_ctx.set("fr")
        try:
            assert get_translation("welcome") == "Bienvenue sur la plateforme Arkidi"
        finally:
            current_language_ctx.reset(token)


class TestExceptionLocalization:
    def test_entity_not_found_french(self):
        exc = EntityNotFoundException("Parish", "p-1")
        assert "p-1" in exc.message
        assert exc.localize("fr") == "Parish avec l'identifiant 'p-1' est introuvable."

    def test_invalid_credentials_uses_request_language(self):
        token = current_language_ctx.set("rw")
        try:
            exc = InvalidCredentialsException()
            assert exc.localize() == "Izina cyangwa ijambobanga ntibikwiye."
        finally:
            current_language_ctx.reset(token)

    def test_permission_denied_with_params(self):
        exc = PermissionDeniedException(
            "Access forbidden. Required roles: SUPER_ADMIN",
            message_key="errors.access_forbidden_roles",
            message_params={"roles": "SUPER_ADMIN"},
        )
        assert exc.localize("fr") == "Accès interdit. Rôles requis : SUPER_ADMIN"

    def test_duplicate_upi_key_is_registered(self):
        exc = DuplicateUPIException("1/02/07")
        translated = exc.localize("rw")
        assert "1/02/07" in translated
        assert translated != "1/02/07"


class TestResponseEnvelopeLocalization:
    def test_ok_message_translated(self):
        token = current_language_ctx.set("fr")
        try:
            response = ApiResponse.ok(message="success.login_successful")
            assert response.message == "Connexion réussie"
        finally:
            current_language_ctx.reset(token)

    def test_ok_plain_message_passes_through(self):
        assert ApiResponse.ok(message="Custom message").message == "Custom message"

    def test_ok_interpolated(self):
        token = current_language_ctx.set("en")
        try:
            response = ApiResponse.ok(
                message="success.amendment_reviewed",
                message_params={"action": "approve"},
            )
            assert response.message == "Amendment approved successfully"
        finally:
            current_language_ctx.reset(token)
