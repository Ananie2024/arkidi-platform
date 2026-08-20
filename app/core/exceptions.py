"""
Core Exception Definitions and Handlers
"""
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse


class ArkidiBaseException(Exception):
    """Base exception for all domain and application errors."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(ArkidiBaseException):
    """Raised when a requested resource is not found."""
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"entity": entity_name, "identifier": str(identifier)},
        )


class PermissionDeniedException(ArkidiBaseException):
    """Raised when user lacks required ecclesiastical or system privileges."""
    def __init__(self, message: str = "Permission denied for this operation."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class CanonicalRuleViolationException(ArkidiBaseException):
    """Raised when an operation violates Roman Catholic canon law rules."""
    def __init__(self, rule_description: str):
        super().__init__(
            message=f"Canonical Rule Violation: {rule_description}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"type": "canonical_violation"},
        )


# ---------------------------------------------------------------------------
# Domain-specific exceptions (consolidated from module-level exception files)
# ---------------------------------------------------------------------------

class InvalidCredentialsException(ArkidiBaseException):
    """Raised when authentication credentials are invalid."""
    def __init__(self, message: str = "Invalid username or password."):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class UserAlreadyExistsException(ArkidiBaseException):
    """Raised when registering a user whose email/username already exists."""
    def __init__(self, message: str = "A user with this email or username already exists."):
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class UserNotFoundException(ArkidiBaseException):
    """Raised when a user account is not found."""
    def __init__(self, message: str = "User account was not found."):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class FaithfulNotFoundException(ArkidiBaseException):
    """Raised when a faithful record is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Faithful with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DuplicateRegistrationNumberException(ArkidiBaseException):
    """Raised when a faithful registration number already exists."""
    def __init__(self, registration_number: str):
        super().__init__(
            message=f"Registration number '{registration_number}' is already in use.",
            status_code=status.HTTP_409_CONFLICT,
        )


class PriestNotFoundException(ArkidiBaseException):
    """Raised when a priest/clergy profile is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Priest with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DeaneryNotFoundException(ArkidiBaseException):
    """Raised when a deanery is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Deanery with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ParishNotFoundException(ArkidiBaseException):
    """Raised when a parish is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Parish with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ParcelNotFoundException(ArkidiBaseException):
    """Raised when a land parcel is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Land parcel with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DuplicateUPIException(ArkidiBaseException):
    """Raised when a cadastral UPI already exists."""
    def __init__(self, upi: str):
        super().__init__(
            message=f"Land parcel UPI '{upi}' is already registered.",
            status_code=status.HTTP_409_CONFLICT,
        )


class SacramentRecordNotFoundException(ArkidiBaseException):
    """Raised when a sacrament registry record is not found."""
    def __init__(self, message: str = "Sacrament registry record was not found."):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class CanonicalImpedimentException(ArkidiBaseException):
    """Raised when a canonical impediment blocks a sacramental act."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Canonical Impediment: {reason}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class CertificateInvalidException(ArkidiBaseException):
    """Raised when a certificate verification token is invalid."""
    def __init__(self, message: str = "Certificate verification token is invalid or expired."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class IntentionNotFoundException(ArkidiBaseException):
    """Raised when a mass intention record is not found."""
    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Mass intention with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """Registers custom exception handlers on FastAPI application."""

    @app.exception_handler(ArkidiBaseException)
    async def arkidi_exception_handler(request: Request, exc: ArkidiBaseException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": exc.message,
                    "type": exc.__class__.__name__,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": str(exc.detail),
                    "type": "HTTPException",
                    "details": {},
                },
            },
        )
