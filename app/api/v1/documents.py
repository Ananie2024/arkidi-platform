"""
Documents Module FastAPI Endpoints
Generic Archdiocesan Digital Document Registry & Document Types
"""

import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import enforce_parish_scope, get_db, require_roles
from app.models.enums import UserRole
from app.models.parcel import LandParcel
from app.schemas.document import (
    DocumentBase,
    DocumentCreate,
    DocumentDispositionReview,
    DocumentResponse,
    DocumentTypeCreate,
    DocumentTypeResponse,
    DocumentTypeUpdate,
    DocumentUpdate,
)
from app.services.document import DocumentService
from app.utils.audit import record_audit_event
from app.utils.response import ApiResponse

router = APIRouter(prefix="/documents", tags=["Documents & Archival Repository"])


async def _enforce_document_scope(db: AsyncSession, user: dict, item: DocumentResponse) -> None:
    if item.parcel_id is not None:
        parcel = await db.scalar(
            select(LandParcel).where(
                LandParcel.id == item.parcel_id, LandParcel.is_deleted.is_(False)
            )
        )
        if parcel is None:
            from app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("errors.parcel_not_found")
        if item.parish_id is not None and item.parish_id != parcel.parish_id:
            from app.core.exceptions import PermissionDeniedException

            raise PermissionDeniedException("Document parish and parcel scopes do not match.")
        await enforce_parish_scope(user, db, parcel.parish_id)
    elif item.parish_id is not None:
        await enforce_parish_scope(user, db, item.parish_id)
    elif user.get("parish_id") or user.get("deanery_id"):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("Access forbidden outside assigned parish.")
    else:
        await enforce_parish_scope(user, db, None)


# ---------------------------------------------------------------------------
# Document Types Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/types",
    response_model=ApiResponse[DocumentTypeResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_document_type(
    data: DocumentTypeCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Create a new official document category/type."""
    service = DocumentService(db)
    created = await service.create_document_type(data)
    return ApiResponse.ok(data=created, message="success.document_type_created")


@router.get("/types", response_model=ApiResponse[list[DocumentTypeResponse]])
async def list_document_types(
    category: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """List all configured document types."""
    service = DocumentService(db)
    items = await service.list_document_types(category=category, is_active=is_active)
    return ApiResponse.ok(data=items)


@router.get("/types/{type_id}", response_model=ApiResponse[DocumentTypeResponse])
async def get_document_type(
    type_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get single document type detail."""
    service = DocumentService(db)
    item = await service.get_document_type(type_id)
    return ApiResponse.ok(data=item)


@router.put("/types/{type_id}", response_model=ApiResponse[DocumentTypeResponse])
async def update_document_type(
    type_id: uuid.UUID,
    data: DocumentTypeUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Update document type."""
    service = DocumentService(db)
    updated = await service.update_document_type(type_id, data)
    return ApiResponse.ok(data=updated, message="success.document_type_updated")


# ---------------------------------------------------------------------------
# Generic Document Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/upload",
    response_model=ApiResponse[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    title: str = Form(...),
    document_type_id: uuid.UUID | None = Form(None),
    classification: str = Form("OFFICIAL"),
    notes: str | None = Form(None),
    archdiocese_id: uuid.UUID | None = Form(None),
    deanery_id: uuid.UUID | None = Form(None),
    parish_id: uuid.UUID | None = Form(None),
    commission_id: uuid.UUID | None = Form(None),
    council_id: uuid.UUID | None = Form(None),
    meeting_id: uuid.UUID | None = Form(None),
    priest_id: uuid.UUID | None = Form(None),
    parcel_id: uuid.UUID | None = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Upload a file and register document with hierarchy scoping."""
    scopes = [
        archdiocese_id,
        deanery_id,
        parish_id,
        commission_id,
        council_id,
        meeting_id,
        priest_id,
        parcel_id,
    ]
    if not any(scopes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="errors.scoping_fk_required",
        )

    metadata = DocumentBase(
        title=title,
        document_type_id=document_type_id,
        classification=classification,
        notes=notes,
        archdiocese_id=archdiocese_id,
        deanery_id=deanery_id,
        parish_id=parish_id,
        commission_id=commission_id,
        council_id=council_id,
        meeting_id=meeting_id,
        priest_id=priest_id,
        parcel_id=parcel_id,
    )

    uploader_id = uuid.UUID(user_payload["sub"]) if user_payload and "sub" in user_payload else None
    if parcel_id is not None:
        parcel = await db.scalar(
            select(LandParcel).where(LandParcel.id == parcel_id, LandParcel.is_deleted.is_(False))
        )
        if parcel is None:
            from app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("errors.parcel_not_found")
        if parish_id is not None and parish_id != parcel.parish_id:
            from app.core.exceptions import ValidationException

            raise ValidationException("Parcel and parish scope do not match.")
        await enforce_parish_scope(user_payload, db, parcel.parish_id)
    elif parish_id is not None:
        await enforce_parish_scope(user_payload, db, parish_id)
    else:
        await enforce_parish_scope(user_payload, db, None)
    service = DocumentService(db)
    created = await service.upload_and_create(
        file=file, metadata=metadata, uploaded_by_user_id=uploader_id
    )
    return ApiResponse.ok(data=created, message="success.document_uploaded")


@router.post(
    "",
    response_model=ApiResponse[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_document_record(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Create a document record referencing an existing storage path."""
    uploader_id = uuid.UUID(user_payload["sub"]) if user_payload and "sub" in user_payload else None
    if data.parish_id is not None:
        await enforce_parish_scope(user_payload, db, data.parish_id)
    else:
        await enforce_parish_scope(user_payload, db, None)
    service = DocumentService(db)
    created = await service.create_document(data, uploaded_by_user_id=uploader_id)
    return ApiResponse.ok(data=created, message="success.document_registered")


@router.get("", response_model=ApiResponse[list[DocumentResponse]])
async def list_documents(
    archdiocese_id: uuid.UUID | None = Query(default=None),
    deanery_id: uuid.UUID | None = Query(default=None),
    parish_id: uuid.UUID | None = Query(default=None),
    commission_id: uuid.UUID | None = Query(default=None),
    council_id: uuid.UUID | None = Query(default=None),
    meeting_id: uuid.UUID | None = Query(default=None),
    priest_id: uuid.UUID | None = Query(default=None),
    parcel_id: uuid.UUID | None = Query(default=None),
    document_type_id: uuid.UUID | None = Query(default=None),
    classification: str | None = Query(default=None),
    search: str | None = Query(default=None),
    disposition_status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    if parcel_id is not None:
        parcel = await db.scalar(
            select(LandParcel).where(LandParcel.id == parcel_id, LandParcel.is_deleted.is_(False))
        )
        if parcel is None:
            from app.core.exceptions import EntityNotFoundException

            raise EntityNotFoundException("errors.parcel_not_found")
        if parish_id is not None and parish_id != parcel.parish_id:
            from app.core.exceptions import ValidationException

            raise ValidationException("Parcel and parish scope do not match.")
        await enforce_parish_scope(user, db, parcel.parish_id)
    else:
        parish_id = await enforce_parish_scope(user, db, parish_id)
    """List documents with comprehensive scoping filters."""
    service = DocumentService(db)
    items = await service.list_documents(
        archdiocese_id=archdiocese_id,
        deanery_id=deanery_id,
        parish_id=parish_id,
        commission_id=commission_id,
        council_id=council_id,
        meeting_id=meeting_id,
        priest_id=priest_id,
        parcel_id=parcel_id,
        document_type_id=document_type_id,
        classification=classification,
        search=search,
        disposition_status=disposition_status,
    )
    for item in items:
        await _enforce_document_scope(db, user, item)
    return ApiResponse.ok(data=items)


@router.get("/{document_id}", response_model=ApiResponse[DocumentResponse])
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get metadata for a single document."""
    service = DocumentService(db)
    item = await service.get_document(document_id)
    await _enforce_document_scope(db, user, item)
    return ApiResponse.ok(data=item)


@router.get("/{document_id}/download")
async def download_document_file(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Download physical file associated with document."""
    service = DocumentService(db)
    doc = await service.get_document(document_id)
    await _enforce_document_scope(db, user, doc)
    full_path = await service.get_physical_path(document_id)
    if not os.path.isfile(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="errors.physical_file_not_found"
        )
    record_audit_event(
        db,
        action="DOCUMENT_DOWNLOADED",
        entity_name="document",
        entity_id=doc.id,
        details={"classification": doc.classification},
    )

    filename = os.path.basename(doc.file_path)
    return FileResponse(
        path=full_path,
        media_type=doc.mime_type or "application/octet-stream",
        filename=filename,
    )


@router.post("/{document_id}/disposition", response_model=ApiResponse[DocumentResponse])
async def review_document_disposition(
    document_id: uuid.UUID,
    review: DocumentDispositionReview,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(
        require_roles(
            [
                UserRole.SUPER_ADMIN,
                UserRole.ARCHBISHOP,
                UserRole.CHANCELLOR,
                UserRole.PARISH_PRIEST,
            ]
        )
    ),
):
    service = DocumentService(db)
    existing = await service.get_document(document_id)
    await _enforce_document_scope(db, user, existing)
    reviewed = await service.review_disposition(document_id, review, uuid.UUID(user["sub"]))
    return ApiResponse.ok(data=reviewed, message="success.document_disposition_reviewed")


@router.put("/{document_id}", response_model=ApiResponse[DocumentResponse])
async def update_document(
    document_id: uuid.UUID,
    data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Update document metadata or scoping."""
    service = DocumentService(db)
    existing = await service.get_document(document_id)
    await _enforce_document_scope(db, user, existing)
    if "parish_id" in data.model_fields_set and data.parish_id is not None:
        await enforce_parish_scope(user, db, data.parish_id)
    elif "parish_id" in data.model_fields_set and (user.get("parish_id") or user.get("deanery_id")):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException(
            "Parish users must keep documents attached to their parish."
        )
    updated = await service.update_document(document_id, data)
    return ApiResponse.ok(data=updated, message="success.document_updated")


@router.delete("/{document_id}", response_model=ApiResponse[dict])
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.CHANCELLOR])),
):
    """Soft delete a document record."""
    service = DocumentService(db)
    existing = await service.get_document(document_id)
    await _enforce_document_scope(db, user, existing)
    await service.delete_document(document_id)
    return ApiResponse.ok(message="success.document_deleted", data={"deleted": True})
