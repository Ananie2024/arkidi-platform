"""
Documents Module FastAPI Endpoints
Generic Archdiocesan Digital Document Registry & Document Types
"""
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentTypeCreate,
    DocumentTypeUpdate,
    DocumentTypeResponse,
    DocumentBase,
)
from app.services.document import DocumentService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/documents", tags=["Documents & Archival Repository"])


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


@router.get("/types", response_model=ApiResponse[List[DocumentTypeResponse]])
async def list_document_types(
    category: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
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
    document_type_id: Optional[uuid.UUID] = Form(None),
    classification: str = Form("OFFICIAL"),
    notes: Optional[str] = Form(None),
    archdiocese_id: Optional[uuid.UUID] = Form(None),
    deanery_id: Optional[uuid.UUID] = Form(None),
    parish_id: Optional[uuid.UUID] = Form(None),
    commission_id: Optional[uuid.UUID] = Form(None),
    council_id: Optional[uuid.UUID] = Form(None),
    meeting_id: Optional[uuid.UUID] = Form(None),
    priest_id: Optional[uuid.UUID] = Form(None),
    parcel_id: Optional[uuid.UUID] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Upload a file and register document with hierarchy scoping."""
    scopes = [
        archdiocese_id, deanery_id, parish_id, commission_id,
        council_id, meeting_id, priest_id, parcel_id,
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
    service = DocumentService(db)
    created = await service.upload_and_create(file=file, metadata=metadata, uploaded_by_user_id=uploader_id)
    return ApiResponse.ok(data=created, message="success.document_uploaded")


@router.post(
    "",
    response_model=ApiResponse[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_document_record(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    user_payload: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Create a document record referencing an existing storage path."""
    uploader_id = uuid.UUID(user_payload["sub"]) if user_payload and "sub" in user_payload else None
    service = DocumentService(db)
    created = await service.create_document(data, uploaded_by_user_id=uploader_id)
    return ApiResponse.ok(data=created, message="success.document_registered")


@router.get("", response_model=ApiResponse[List[DocumentResponse]])
async def list_documents(
    archdiocese_id: Optional[uuid.UUID] = Query(default=None),
    deanery_id: Optional[uuid.UUID] = Query(default=None),
    parish_id: Optional[uuid.UUID] = Query(default=None),
    commission_id: Optional[uuid.UUID] = Query(default=None),
    council_id: Optional[uuid.UUID] = Query(default=None),
    meeting_id: Optional[uuid.UUID] = Query(default=None),
    priest_id: Optional[uuid.UUID] = Query(default=None),
    parcel_id: Optional[uuid.UUID] = Query(default=None),
    document_type_id: Optional[uuid.UUID] = Query(default=None),
    classification: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
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
    )
    return ApiResponse.ok(data=items)


@router.get("/{document_id}", response_model=ApiResponse[DocumentResponse])
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Get metadata for a single document."""
    service = DocumentService(db)
    item = await service.get_document(document_id)
    return ApiResponse.ok(data=item)


@router.get("/{document_id}/download")
async def download_document_file(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Download physical file associated with document."""
    service = DocumentService(db)
    full_path = await service.get_physical_path(document_id)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="errors.physical_file_not_found")

    doc = await service.get_document(document_id)
    filename = os.path.basename(doc.file_path)
    return FileResponse(
        path=full_path,
        media_type=doc.mime_type or "application/octet-stream",
        filename=filename,
    )


@router.put("/{document_id}", response_model=ApiResponse[DocumentResponse])
async def update_document(
    document_id: uuid.UUID,
    data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    """Update document metadata or scoping."""
    service = DocumentService(db)
    updated = await service.update_document(document_id, data)
    return ApiResponse.ok(data=updated, message="success.document_updated")


@router.delete("/{document_id}", response_model=ApiResponse[dict])
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.CHANCELLOR])),
):
    """Soft delete a document record."""
    service = DocumentService(db)
    await service.delete_document(document_id)
    return ApiResponse.ok(message="success.document_deleted", data={"deleted": True})
