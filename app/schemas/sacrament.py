"""
Sacraments Module Pydantic v2 Schemas
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.sacrament import (
    AmendmentStatus,
    AmendmentType,
    HolyOrdersOrderType,
    ReligiousProfessionType,
    SacramentType,
)


class BaptismBase(BaseModel):
    registry_year: int
    volume_number: str
    page_number: str
    act_number: str
    celebration_date: date
    minister_name: str
    godfather_name: str | None = None
    godmother_name: str | None = None
    marginal_notes: str | None = None


class BaptismCreate(BaptismBase):
    parish_id: uuid.UUID
    faithful_id: uuid.UUID


class BaptismResponse(BaptismBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    faithful_id: uuid.UUID
    created_at: datetime


class ConfirmationBase(BaseModel):
    registry_year: int
    volume_number: str
    page_number: str
    act_number: str
    celebration_date: date
    administering_bishop_or_vicar: str
    sponsor_name: str | None = None


class ConfirmationCreate(ConfirmationBase):
    parish_id: uuid.UUID
    faithful_id: uuid.UUID


class ConfirmationResponse(ConfirmationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    faithful_id: uuid.UUID
    created_at: datetime


class MatrimonyBase(BaseModel):
    registry_year: int
    volume_number: str
    page_number: str
    act_number: str
    celebration_date: date
    priest_celebrant: str
    witness_1_name: str
    witness_2_name: str
    dispensations_or_canonical_notes: str | None = None


class MatrimonyCreate(MatrimonyBase):
    parish_id: uuid.UUID
    groom_faithful_id: uuid.UUID
    bride_faithful_id: uuid.UUID


class MatrimonyResponse(MatrimonyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    groom_faithful_id: uuid.UUID
    bride_faithful_id: uuid.UUID
    created_at: datetime


class FirstCommunionBase(BaseModel):
    registry_year: int
    volume_number: str
    page_number: str
    act_number: str
    celebration_date: date
    celebrant_name: str
    catechetical_program_name: str | None = None
    sponsor_name: str | None = None
    marginal_notes: str | None = None


class FirstCommunionCreate(FirstCommunionBase):
    parish_id: uuid.UUID
    faithful_id: uuid.UUID


class FirstCommunionResponse(FirstCommunionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    faithful_id: uuid.UUID
    created_at: datetime


class HolyOrdersBase(BaseModel):
    page_number: str
    act_number: str
    ordination_date: date
    order_type: HolyOrdersOrderType
    ordaining_prelate: str
    diocese_of_incardination: str | None = None
    permanent: bool = True
    marginal_notes: str | None = None


class HolyOrdersCreate(HolyOrdersBase):
    parish_id: uuid.UUID
    ordained_faithful_id: uuid.UUID


class HolyOrdersResponse(HolyOrdersBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    ordained_faithful_id: uuid.UUID
    created_at: datetime


class ReligiousProfessionBase(BaseModel):
    page_number: str
    act_number: str
    profession_date: date
    profession_type: ReligiousProfessionType
    congregation_or_institute: str
    superior_name: str | None = None
    marginal_notes: str | None = None


class ReligiousProfessionCreate(ReligiousProfessionBase):
    parish_id: uuid.UUID
    professed_faithful_id: uuid.UUID


class ReligiousProfessionResponse(ReligiousProfessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    professed_faithful_id: uuid.UUID
    created_at: datetime


class AnointingOfTheSickBase(BaseModel):
    anointing_date: date
    minister_name: str
    place_of_anointing: str | None = None
    notes: str | None = None


class AnointingOfTheSickCreate(AnointingOfTheSickBase):
    parish_id: uuid.UUID
    faithful_id: uuid.UUID


class AnointingOfTheSickResponse(AnointingOfTheSickBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    faithful_id: uuid.UUID
    created_at: datetime


class ChristianFuneralBase(BaseModel):
    date_of_death: date
    funeral_date: date
    burial_site: str | None = None
    officiating_priest: str
    last_sacraments_received: bool = False
    notes: str | None = None


class ChristianFuneralCreate(ChristianFuneralBase):
    parish_id: uuid.UUID
    deceased_faithful_id: uuid.UUID


class ChristianFuneralResponse(ChristianFuneralBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    deceased_faithful_id: uuid.UUID
    created_at: datetime


class CertificateRequest(BaseModel):
    sacrament_type: SacramentType
    faithful_id: uuid.UUID
    parish_id: uuid.UUID


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    certificate_number: str
    sacrament_type: SacramentType
    faithful_id: uuid.UUID
    parish_id: uuid.UUID
    verification_token: str
    qr_code_base64: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Sacramental Amendment Workflow Schemas
# ---------------------------------------------------------------------------


class AmendmentRequestCreate(BaseModel):
    sacrament_type: SacramentType
    record_id: uuid.UUID
    amendment_type: AmendmentType = AmendmentType.CLERICAL_ERROR
    reason: str = Field(min_length=5, description="Canonical justification for correction")
    field_changes: dict = Field(
        ...,
        description="Structured dictionary of field modifications with old and new values",
    )
    supporting_document_id: uuid.UUID | None = None


class AmendmentReviewRequest(BaseModel):
    action: str = Field(pattern="^(APPROVE|REJECT)$", description="'APPROVE' or 'REJECT'")
    review_notes: str | None = None


class SacramentalAmendmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sacrament_type: SacramentType
    record_id: uuid.UUID
    amendment_type: AmendmentType
    reason: str
    field_changes: dict
    supporting_document_id: uuid.UUID | None = None
    status: AmendmentStatus
    requested_by_user_id: uuid.UUID | None = None
    reviewed_by_user_id: uuid.UUID | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    created_at: datetime
    updated_at: datetime
