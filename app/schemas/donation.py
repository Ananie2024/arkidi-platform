"""
Finance Module Pydantic v2 Schemas
"""
import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.donation import DonationType, PaymentMethod


class DonationBase(BaseModel):
    donation_type: DonationType = DonationType.TITHE
    payment_method: PaymentMethod = PaymentMethod.CASH
    amount: float
    currency: str = "RWF"
    donation_date: date
    donor_name_override: Optional[str] = None
    reference_transaction_id: Optional[str] = None
    notes: Optional[str] = None


class DonationCreate(DonationBase):
    parish_id: uuid.UUID
    faithful_id: Optional[uuid.UUID] = None
    family_id: Optional[uuid.UUID] = None


class DonationResponse(DonationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    receipt_number: str
    parish_id: uuid.UUID
    faithful_id: Optional[uuid.UUID] = None
    family_id: Optional[uuid.UUID] = None
    created_at: datetime


class FinancialSummaryResponse(BaseModel):
    total_tithes: float
    total_offertory: float
    total_construction: float
    grand_total: float
    currency: str = "RWF"
