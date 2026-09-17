"""
Core Exception Definitions and Handlers

All API-facing error messages are resolved through the backend i18n message
catalog (``app/locales/<lang>/messages.json``) so they respect the language
detected by ``LanguageMiddleware`` (``Accept-Language`` header or ``?lang=``).
"""
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.utils.i18n import get_translation, is_translation_key


class ArkidiBaseException(Exception):
    """Base exception for all domain and application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
        *,
        message_key: Optional[str] = None,
        message_params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        # A catalog key (e.g. "errors.parish_not_found") may be passed either
        # explicitly or as the message string itself. Literal English text is
        # kept as-is for full backward compatibility.
        if message_key is not None:
            self.message_key = message_key
            self.message_params = message_params or {}
        elif is_translation_key(message):
            self.message_key = message
            self.message_params = message_params or {}
        else:
            self.message_key = None
            self.message_params = {}

    def localize(self, lang: Optional[str] = None) -> str:
        """Return the message for the active (or explicit) request language.

        The English message stored on the exception is used as a fallback when
        a translation key is missing from the catalog, so existing consumers
        (logs, tests) keep seeing useful text.
        """
        if self.message_key is not None:
            return get_translation(
                self.message_key,
                self.message_params,
                default=self.message,
                lang=lang,
            )
        return self.message


class EntityNotFoundException(ArkidiBaseException):
    """Raised when a requested resource is not found."""
    def __init__(self, message_or_entity: str, identifier: Optional[Any] = None):
        if identifier is not None:
            message = f"{message_or_entity} with identifier '{identifier}' was not found."
            details = {"entity": message_or_entity, "identifier": str(identifier)}
            super().__init__(
                message=message,
                status_code=status.HTTP_404_NOT_FOUND,
                details=details,
                message_key="errors.entity_not_found",
                message_params={"entity": message_or_entity, "identifier": str(identifier)},
            )
        else:
            # No identifier: the single argument is either a catalog key
            # (e.g. "errors.survey_not_found") or a literal message. The base
            # class resolves catalog keys against the request language.
            super().__init__(
                message=message_or_entity,
                status_code=status.HTTP_404_NOT_FOUND,
            )


class ValidationException(ArkidiBaseException):
    """Raised when request payload or business rule validation fails."""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        *,
        message_key: Optional[str] = None,
        message_params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details or {},
            message_key=message_key,
            message_params=message_params,
        )


class PermissionDeniedException(ArkidiBaseException):
    """Raised when user lacks required ecclesiastical or system privileges."""
    def __init__(
        self,
        message: str = "Permission denied for this operation.",
        *,
        message_key: Optional[str] = None,
        message_params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            message_key=message_key or "errors.permission_denied",
            message_params=message_params,
        )


class CanonicalRuleViolationException(ArkidiBaseException):
    """Raised when an operation violates Roman Catholic canon law rules."""
    def __init__(self, rule_description: str):
        super().__init__(
            message=f"Canonical Rule Violation: {rule_description}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"type": "canonical_violation"},
            message_key="errors.canonical_rule_violation",
            message_params={"rule": rule_description},
        )


# ---------------------------------------------------------------------------
# Domain-specific exceptions (consolidated from module-level exception files)
# ---------------------------------------------------------------------------

class InvalidCredentialsException(ArkidiBaseException):
    """Raised when authentication credentials are invalid."""
    def __init__(self, message: Optional[str] = None, *, message_key: Optional[str] = None, message_params: Optional[Dict[str, Any]] = None):
        if message is None:
            message = "Invalid username or password."
            message_key = message_key or "errors.invalid_credentials"
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message_key=message_key,
            message_params=message_params,
        )


class UserAlreadyExistsException(ArkidiBaseException):
    """Raised when registering a user whose email/username already exists."""
    def __init__(self, message: Optional[str] = None, *, message_key: Optional[str] = None, message_params: Optional[Dict[str, Any]] = None):
        if message is None:
            message = "A user with this email or username already exists."
            message_key = message_key or "errors.user_already_exists"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            message_key=message_key,
            message_params=message_params,
        )


class UserNotFoundException(ArkidiBaseException):
    """Raised when a user account is not found."""
    def __init__(self, message: str = "User account was not found."):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            message_key="errors.user_not_found",
        )


class InvalidResetTokenException(ArkidiBaseException):
    """Raised when a password-reset token is invalid, expired, or already consumed."""
    def __init__(self, message: str = "The password reset link is invalid or has expired."):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            message_key="errors.invalid_reset_token",
        )


class FaithfulNotFoundException(ArkidiBaseException):
    """Raised when a faithful record is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Faithful with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            message_key="errors.faithful_not_found",
            message_params={"identifier": str(identifier)},
        )


class DuplicateRegistrationNumberException(ArkidiBaseException):
    """Raised when a faithful registration number already exists."""
    def __init__(self, registration_number: str):
        super().__init__(
            message=f"Registration number '{registration_number}' is already in use.",
            status_code=status.HTTP_409_CONFLICT,
            message_key="errors.duplicate_registration_number",
            message_params={"registration_number": str(registration_number)},
        )


class PriestNotFoundException(ArkidiBaseException):
    """Raised when a priest/clergy profile is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Priest with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            message_key="errors.priest_not_found",
            message_params={"identifier": str(identifier)},
        )


class DeaneryNotFoundException(ArkidiBaseException):
    """Raised when a deanery is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Deanery with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            message_key="errors.deanery_not_found",
            message_params={"identifier": str(identifier)},
        )


class ParishNotFoundException(ArkidiBaseException):
    """Raised when a parish is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Parish with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            message_key="errors.parish_not_found",
            message_params={"identifier": str(identifier)},
        )


class ParcelNotFoundException(ArkidiBaseException):
    """Raised when a land parcel is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Land parcel with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            message_key="errors.parcel_not_found",
            message_params={"identifier": str(identifier)},
        )


class DuplicateUPIException(ArkidiBaseException):
    """Raised when a cadastral UPI already exists."""
    def __init__(self, upi: str):
        super().__init__(
            message=f"Land parcel UPI '{upi}' is already registered.",
            status_code=status.HTTP_409_CONFLICT,
            message_key="errors.duplicate_upi",
            message_params={"upi": str(upi)},
        )


class DuplicateDocumentException(ArkidiBaseException):
    """Raised when the same document content is already archived.

    The archive is content-addressed: identical bytes (same SHA-256 checksum)
    must never be registered twice, so re-uploading the same file is rejected.
    """
    def __init__(self, checksum: str):
        super().__init__(
            message=f"A document with checksum '{checksum}' is already archived.",
            status_code=status.HTTP_409_CONFLICT,
            details={"checksum": str(checksum), "type": "duplicate_document"},
            message_key="errors.document_duplicate",
            message_params={"checksum": str(checksum)},
        )


class DuplicateLedgerBookException(ArkidiBaseException):
    """Raised when a physical canonical ledger book already exists for a parish.

    A ledger book is uniquely identified by (parish, sacrament type, volume).
    """
    def __init__(self, parish_id, sacrament_type, volume_number: str):
        super().__init__(
            message=(
                f"A ledger book for parish '{parish_id}', sacrament "
                f"'{sacrament_type}' and volume '{volume_number}' already exists."
            ),
            status_code=status.HTTP_409_CONFLICT,
            details={
                "parish_id": str(parish_id),
                "sacrament_type": str(sacrament_type),
                "volume_number": str(volume_number),
                "type": "duplicate_ledger_book",
            },
            message_key="errors.ledger_book_duplicate",
            message_params={
                "parish_id": str(parish_id),
                "sacrament_type": str(sacrament_type),
                "volume_number": str(volume_number),
            },
        )


class DuplicateScannedPageException(ArkidiBaseException):
    """Raised when a page of a ledger book is scanned more than once."""
    def __init__(self, ledger_book_id, page_number: int):
        super().__init__(
            message=(
                f"Page '{page_number}' is already scanned for ledger book "
                f"'{ledger_book_id}'."
            ),
            status_code=status.HTTP_409_CONFLICT,
            details={
                "ledger_book_id": str(ledger_book_id),
                "page_number": int(page_number),
                "type": "duplicate_scanned_page",
            },
            message_key="errors.scanned_page_duplicate",
            message_params={
                "ledger_book_id": str(ledger_book_id),
                "page_number": int(page_number),
            },
        )


class SacramentRecordNotFoundException(ArkidiBaseException):
    """Raised when a sacrament registry record is not found."""
    def __init__(self, message: str = "Sacrament registry record was not found."):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            message_key="errors.sacrament_record_not_found",
        )


class CanonicalImpedimentException(ArkidiBaseException):
    """Raised when a canonical impediment blocks a sacramental act."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Canonical Impediment: {reason}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message_key="errors.canonical_impediment",
            message_params={"reason": reason},
        )


class CertificateInvalidException(ArkidiBaseException):
    """Raised when a certificate verification token is invalid."""
    def __init__(self, message: str = "Certificate verification token is invalid or expired."):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            message_key="errors.certificate_invalid",
        )


class IntentionNotFoundException(ArkidiBaseException):
    """Raised when a mass intention record is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Mass intention with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            message_key="errors.intention_not_found",
            message_params={"identifier": str(identifier)},
        )


class IndicatorNotFoundException(ArkidiBaseException):
    """Raised when a statistic indicator key is not registered."""
    def __init__(self, key: Any):
        super().__init__(
            message=f"Statistic indicator '{key}' is not registered.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"indicator_key": str(key)},
            message_key="errors.indicator_not_found",
            message_params={"key": str(key)},
        )


class IndicatorScopeRequiredException(ArkidiBaseException):
    """Raised when an indicator is computed without any organisational scope."""
    def __init__(self, message: str = "An archdiocese_id or deanery_id scope is required to compute an indicator."):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            message_key="errors.indicator_scope_required",
        )


class GoogleAuthException(ArkidiBaseException):
    """Raised when Google OAuth verification fails."""
    def __init__(self, message: str = "Google authentication failed.", *, message_key: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            message_key=message_key or "errors.google_auth_failed",
        )


class GoogleAccountNotLinkedException(ArkidiBaseException):
    """Raised when a Google user has no associated account in the system."""
    def __init__(self, email: str):
        super().__init__(
            message=f"No system account found for Google email '{email}'. Please contact your administrator.",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"email": email},
            message_key="errors.google_account_not_registered",
            message_params={"email": email},
        )


def _request_language(request: Request) -> Optional[str]:
    """Language detected by ``LanguageMiddleware`` (falls back to the context var)."""
    lang = getattr(request.state, "lang", None)
    return lang or None


def setup_exception_handlers(app: FastAPI) -> None:
    """Registers custom exception handlers on FastAPI application."""

    @app.exception_handler(ArkidiBaseException)
    async def arkidi_exception_handler(request: Request, exc: ArkidiBaseException) -> JSONResponse:
        lang = _request_language(request)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": exc.localize(lang),
                    "type": exc.__class__.__name__,
                    "details": exc.details,
                    "language": lang,
                },
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        lang = _request_language(request)
        detail = exc.detail
        if is_translation_key(detail):
            message = get_translation(detail, default=str(detail), lang=lang)
        else:
            message = str(detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": message,
                    "type": "HTTPException",
                    "details": {},
                    "language": lang,
                },
            },
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        lang = _request_language(request)
        message = get_translation("errors.rate_limit_exceeded", default=f"Rate limit exceeded: {exc.detail}", lang=lang)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "error": {
                    "message": message,
                    "type": "RateLimitExceeded",
                    "details": {"detail": str(exc.detail)},
                    "language": lang,
                },
            },
        )
