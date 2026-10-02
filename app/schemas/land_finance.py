import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LeaseCreate(BaseModel):
    parcel_id: uuid.UUID
    lease_number: str = Field(min_length=1, max_length=50)
    lessee_name: str = Field(min_length=1, max_length=200)
    lessee_contact: str | None = None
    start_date: date
    end_date: date | None = None
    monthly_rent_rwf: float = Field(ge=0)
    contract_document_path: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def valid_term(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("Lease end date must be on or after its start date")
        return self


class LeaseResponse(LeaseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    status: str
    created_at: datetime


class LeaseInstallmentCreate(BaseModel):
    due_date: date
    amount_rwf: float = Field(gt=0)


class LeaseInstallmentResponse(LeaseInstallmentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    lease_agreement_id: uuid.UUID
    is_paid: bool
    paid_date: date | None
    receipt_number: str | None
    created_at: datetime


class LeaseInstallmentPayment(BaseModel):
    paid_date: date
    receipt_number: str = Field(min_length=1, max_length=50)


class TaxAssessmentCreate(BaseModel):
    tax_year: int = Field(ge=1900, le=2200)
    assessed_value_rwf: float = Field(ge=0)
    tax_amount_rwf: float = Field(ge=0)
    assessment_date: date | None = None
    notes: str | None = None


class TaxAssessmentResponse(TaxAssessmentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    parcel_id: uuid.UUID
    status: str
    created_at: datetime


class TaxPaymentCreate(BaseModel):
    amount_paid_rwf: float = Field(gt=0)
    payment_date: date
    payment_method: str = Field(default="CASH", pattern="^(CASH|MOMO|BANK_TRANSFER|CHECK)$")
    receipt_number: str | None = Field(default=None, max_length=50)


class TaxPaymentResponse(TaxPaymentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tax_record_id: uuid.UUID
    created_at: datetime
