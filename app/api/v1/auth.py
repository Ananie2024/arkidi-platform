"""
Auth Module FastAPI Endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user_payload, require_roles
from app.models.enums import UserRole
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth import AuthService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and issue access + refresh JWT tokens."""
    service = AuthService(db)
    tokens = await service.authenticate(credentials)
    return ApiResponse.ok(data=tokens, message="Login successful")


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Register a new system user (admin only)."""
    service = AuthService(db)
    created = await service.register_user(data)
    return ApiResponse.ok(data=created, message="User registered successfully")


@router.get(
    "/me",
    response_model=ApiResponse[dict],
)
async def read_current_user(
    payload: dict = Depends(get_current_user_payload),
):
    """Return the decoded JWT payload of the currently authenticated user."""
    return ApiResponse.ok(data=payload)