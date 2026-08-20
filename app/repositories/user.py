"""
Auth Module Database Repository
"""
import uuid
from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id, User.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        stmt = select(User).where(
            or_(User.username == identifier, User.email == identifier),
            User.is_deleted.is_(False),
        )
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

    async def list_users(self, skip: int = 0, limit: int = 50) -> List[User]:
        stmt = select(User).where(User.is_deleted.is_(False)).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def log_audit(self, action: str, entity_name: str, entity_id: str | None = None, user_id: uuid.UUID | None = None, details: dict | None = None) -> AuditLog:
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
