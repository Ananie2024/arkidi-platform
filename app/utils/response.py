"""
Standard API Response Envelope
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.utils.i18n import get_translation

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: T | None = None

    @classmethod
    def ok(
        cls,
        data: T | None = None,
        message: str = "Success",
        *,
        message_params: dict[str, Any] | None = None,
    ) -> "ApiResponse[T]":
        # Localize catalog keys (e.g. "success.login_successful") against the
        # active request language; plain English messages pass through.
        return cls(
            success=True,
            message=get_translation(message, params=message_params, default=message),
            data=data,
        )

    @classmethod
    def error(  # type: ignore[override]
        cls,
        message: str,
        data: T | None = None,
        *,
        message_params: dict[str, Any] | None = None,
    ) -> "ApiResponse[T]":
        return cls(
            success=False,
            message=get_translation(message, params=message_params, default=message),
            data=data,
        )
