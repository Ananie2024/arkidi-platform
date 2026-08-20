"""
Arkidi Models Package — all ORM models are imported here so that
Alembic autogenerate and the application registry can discover them.
"""
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin
from app.models.enums import UserRole, ROLE_HIERARCHY, has_role
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.appointment import Appointment, AppointmentRole, AppointmentStatus
from app.models.deanery import Archdiocese, Deanery
from app.models.parish import Parish, Centrale, SmallChristianCommunity
from app.models.council import Council, CouncilType
from app.models.commission import Commission, CommissionCategory
from app.models.meeting import Meeting
from app.models.meeting_minute import MeetingMinute
from app.models.document import Document, ArchiveLedgerBook, ScannedPage
from app.models.document_type import DocumentType
from app.models.physical_location import PhysicalLocation
from app.models.qr_code_registry import QrCodeRegistry, QrCodePurpose
from app.models.storage_cabinet import StorageCabinet
from app.models.parcel import LandParcel, LandDocument, BuildingAsset, LandUseType, TenureStatus
from app.models.parcel_ownership_history import ParcelOwnershipHistory
from app.models.lease_agreement import LeaseAgreement
from app.models.lease_payment_schedule import LeasePaymentSchedule
from app.models.tax_record import TaxRecord
from app.models.tax_payment import TaxPayment
from app.models.land_use_category import LandUseCategory
from app.models.faithful import Faithful, Family, Gender, CanonicalStatus, FamilyRole
from app.models.priest import Priest, ClergyAssignment, ClergyType, ClergyStatus
from app.models.ministry import Ministry, MinistryCategory
from app.models.mass import MassSchedule
from app.models.intention import MassIntention, IntentionType
from app.models.donation import Donation, DonationType, PaymentMethod
from app.models.event import Event, EventType
from app.models.survey import Survey, SurveyResponse, AnnualParishStatistic
from app.models.sacrament import (
    SacramentType,
    BaptismRecord,
    ConfirmationRecord,
    MatrimonyRecord,
    FirstCommunionRecord,
    HolyOrdersRecord,
    HolyOrdersOrderType,
    ReligiousProfessionRecord,
    ReligiousProfessionType,
    AnointingOfTheSickRecord,
    ChristianFuneralRecord,
    CertificateIssue,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "SoftDeleteMixin",
    "UserRole",
    "ROLE_HIERARCHY",
    "has_role",
    "User",
    "AuditLog",
    "Appointment",
    "AppointmentRole",
    "AppointmentStatus",
    "Archdiocese",
    "Deanery",
    "Parish",
    "Centrale",
    "SmallChristianCommunity",
    "Council",
    "CouncilType",
    "Commission",
    "CommissionCategory",
    "Meeting",
    "MeetingMinute",
    "Document",
    "DocumentType",
    "ArchiveLedgerBook",
    "ScannedPage",
    "PhysicalLocation",
    "QrCodeRegistry",
    "QrCodePurpose",
    "StorageCabinet",
    "LandParcel",
    "LandDocument",
    "BuildingAsset",
    "LandUseType",
    "TenureStatus",
    "ParcelOwnershipHistory",
    "LeaseAgreement",
    "LeasePaymentSchedule",
    "TaxRecord",
    "TaxPayment",
    "LandUseCategory",
    "Faithful",
    "Family",
    "Gender",
    "CanonicalStatus",
    "FamilyRole",
    "Priest",
    "ClergyAssignment",
    "ClergyType",
    "ClergyStatus",
    "Ministry",
    "MinistryCategory",
    "MassSchedule",
    "MassIntention",
    "IntentionType",
    "Donation",
    "DonationType",
    "PaymentMethod",
    "Event",
    "EventType",
    "Survey",
    "SurveyResponse",
    "AnnualParishStatistic",
    "SacramentType",
    "BaptismRecord",
    "ConfirmationRecord",
    "MatrimonyRecord",
    "FirstCommunionRecord",
    "HolyOrdersRecord",
    "HolyOrdersOrderType",
    "ReligiousProfessionRecord",
    "ReligiousProfessionType",
    "AnointingOfTheSickRecord",
    "ChristianFuneralRecord",
    "CertificateIssue",
]
