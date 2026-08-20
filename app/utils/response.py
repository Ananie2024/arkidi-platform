"""
Standard API Response Envelope
"""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None

    @classmethod
    def ok(cls, data: T = None, message: str = "Success") -> "ApiResponse[T]":
        return cls(success=True, message=message, data=data)

    @classmethod
    def error(cls, message: str, data: Optional[T] = None) -> "ApiResponse[T]":
        return cls(success=False, message=message, data=data)
