"""
Auth Module Database Repository
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.user import UserCreate


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.id == user_id, User.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> User | None:
        stmt = select(User).where(
            or_(User.username == identifier, User.email == identifier),
            User.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Look up an active (non-soft-deleted) user by exact e-mail address."""
        stmt = select(User).where(User.email == email, User.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, data: UserCreate) -> User:
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            phone_number=data.phone_number,
            role=data.role,
            parish_id=data.parish_id,
            deanery_id=data.deanery_id,
            is_active=data.is_active,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def list_users(self, skip: int = 0, limit: int = 50) -> list[User]:
        stmt = select(User).where(User.is_deleted.is_(False)).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_last_login(self, user_id: uuid.UUID) -> User | None:
        """Update a user's last login timestamp and return the updated user."""
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.last_login_at = datetime.now(UTC)
        await self.db.flush()
        return user

    async def update_password(self, user_id: uuid.UUID, hashed_password: str) -> User | None:
        """Update a user's password hash and return the updated user."""
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.hashed_password = hashed_password
        await self.db.flush()
        return user

    async def log_audit(
        self,
        action: str,
        entity_name: str,
        entity_id: str | None = None,
        user_id: uuid.UUID | None = None,
        details: dict | None = None,
    ) -> AuditLog:
        log = AuditLog(
            action=action,
            entity_name=entity_name,
            entity_id=entity_id,
            user_id=user_id,
            details=details,
        )
        self.db.add(log)
        await self.db.flush()
        return log
