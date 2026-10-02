"""
Sacraments Module Business Logic Service
"""

import secrets
import uuid
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    CertificateInvalidException,
    EntityNotFoundException,
    ValidationException,
)
from app.models.audit_log import AuditLog
from app.models.sacrament import (
    AmendmentStatus,
    BaptismRecord,
    CertificateIssue,
    ConfirmationRecord,
    FirstCommunionRecord,
    HolyOrdersRecord,
    MatrimonyRecord,
    ReligiousProfessionRecord,
    SacramentType,
)
from app.repositories.sacrament import SacramentsRepository
from app.schemas.sacrament import (
    AmendmentRequestCreate,
    AmendmentReviewRequest,
    AnointingOfTheSickCreate,
    AnointingOfTheSickResponse,
    BaptismCreate,
    BaptismResponse,
    CertificateRequest,
    CertificateResponse,
    CertificateVerificationResponse,
    ChristianFuneralCreate,
    ChristianFuneralResponse,
    ConfirmationCreate,
    ConfirmationResponse,
    FirstCommunionCreate,
    FirstCommunionResponse,
    HolyOrdersCreate,
    HolyOrdersResponse,
    MatrimonyCreate,
    MatrimonyResponse,
    ReligiousProfessionCreate,
    ReligiousProfessionResponse,
    SacramentalAmendmentResponse,
)
from app.utils.pdf import generate_certificate_pdf
from app.utils.qr import generate_qr_code_base64, generate_qr_code_bytes

SACRAMENT_DISPLAY_NAMES = {
    SacramentType.BAPTISM: "Certificate of Baptism",
    SacramentType.FIRST_COMMUNION: "Certificate of First Communion",
    SacramentType.CONFIRMATION: "Certificate of Confirmation",
    SacramentType.MATRIMONY: "Certificate of Canonical Marriage",
    SacramentType.HOLY_ORDERS: "Certificate of Holy Orders",
    SacramentType.RELIGIOUS_PROFESSION: "Certificate of Religious Profession",
    SacramentType.ANOINTING_OF_THE_SICK: "Certificate of the Anointing of the Sick",
    SacramentType.CHRISTIAN_FUNERAL: "Certificate of Christian Burial",
}

AMENDABLE_FIELDS = {
    SacramentType.BAPTISM: {
        "registry_year", "volume_number", "page_number", "act_number", "celebration_date",
        "minister_name", "godfather_name", "godmother_name",
    },
    SacramentType.CONFIRMATION: {
        "registry_year", "volume_number", "page_number", "act_number", "celebration_date",
        "administering_bishop_or_vicar", "sponsor_name",
    },
    SacramentType.MATRIMONY: {
        "registry_year", "volume_number", "page_number", "act_number", "celebration_date",
        "priest_celebrant", "witness_1_name", "witness_2_name",
        "dispensations_or_canonical_notes",
    },
    SacramentType.FIRST_COMMUNION: {
        "registry_year", "volume_number", "page_number", "act_number", "celebration_date",
        "celebrant_name", "catechetical_program_name", "sponsor_name",
    },
    SacramentType.HOLY_ORDERS: {
        "page_number", "act_number", "ordination_date", "order_type", "ordaining_prelate",
        "diocese_of_incardination", "permanent",
    },
    SacramentType.RELIGIOUS_PROFESSION: {
        "page_number", "act_number", "profession_date", "profession_type",
        "congregation_or_institute", "superior_name",
    },
    SacramentType.ANOINTING_OF_THE_SICK: {
        "anointing_date", "minister_name", "place_of_anointing", "notes",
    },
    SacramentType.CHRISTIAN_FUNERAL: {
        "date_of_death", "funeral_date", "burial_site", "officiating_priest",
        "last_sacraments_received", "notes",
    },
}


def _canonical_value(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "value"):
        return str(value.value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _coerce_amendment_value(current_value: Any, new_value: Any) -> Any:
    if new_value is None:
        return None
    if isinstance(current_value, bool):
        if isinstance(new_value, bool):
            return new_value
        return str(new_value).lower() in {"true", "1", "yes"}
    if isinstance(current_value, int) and not isinstance(current_value, bool):
        return int(new_value)
    if isinstance(current_value, date):
        return date.fromisoformat(str(new_value))
    if isinstance(current_value, Enum):
        return type(current_value)(new_value)
    return str(new_value)


class SacramentsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SacramentsRepository(db)

    def _audit_record_created(
        self,
        record: Any,
        sacrament_type: SacramentType,
        actor_id: uuid.UUID | None,
    ) -> None:
        reference_fields = (
            ("registry_year", "volume_number", "page_number", "act_number")
            if hasattr(record, "registry_year")
            else (("register_book", "page_number", "act_number") if hasattr(record, "register_book") else ())
        )
        self.db.add(
            AuditLog(
                user_id=actor_id,
                action="SACRAMENTAL_RECORD_CREATED",
                entity_name=sacrament_type.value,
                entity_id=str(record.id),
                details={
                    "parish_id": str(record.parish_id),
                    "register_reference": {
                        field: _canonical_value(getattr(record, field))
                        for field in reference_fields
                    },
                },
            )
        )

    async def _ensure_register_reference_available(
        self, model: type, data: Any, fields: tuple[str, ...]
    ) -> None:
        reference = {field: getattr(data, field) for field in fields}
        if await self.repo.register_reference_exists(model, reference):
            reference_text = "/".join(str(value) for value in reference.values())
            raise ValidationException(
                "This canonical register reference is already in use.",
                message_key="errors.sacramental_register_reference_exists",
                message_params={"reference": reference_text},
            )

    async def list_baptisms(self, parish_id: uuid.UUID | None = None) -> list[BaptismResponse]:
        records = await self.repo.list_baptisms(parish_id=parish_id)
        return [BaptismResponse.model_validate(record) for record in records]

    async def record_baptism(
        self, data: BaptismCreate, created_by_user_id: uuid.UUID | None = None
    ) -> BaptismResponse:
        await self._ensure_register_reference_available(
            BaptismRecord, data, ("parish_id", "registry_year", "volume_number", "act_number")
        )
        record = await self.repo.create_baptism(data)
        self._audit_record_created(record, SacramentType.BAPTISM, created_by_user_id)
        return BaptismResponse.model_validate(record)

    async def list_confirmations(
        self, parish_id: uuid.UUID | None = None
    ) -> list[ConfirmationResponse]:
        records = await self.repo.list_confirmations(parish_id=parish_id)
        return [ConfirmationResponse.model_validate(record) for record in records]

    async def record_confirmation(
        self, data: ConfirmationCreate, created_by_user_id: uuid.UUID | None = None
    ) -> ConfirmationResponse:
        await self._ensure_register_reference_available(
            ConfirmationRecord, data, ("parish_id", "registry_year", "volume_number", "act_number")
        )
        record = await self.repo.create_confirmation(data)
        self._audit_record_created(record, SacramentType.CONFIRMATION, created_by_user_id)
        return ConfirmationResponse.model_validate(record)

    async def list_matrimonies(self, parish_id: uuid.UUID | None = None) -> list[MatrimonyResponse]:
        records = await self.repo.list_matrimonies(parish_id=parish_id)
        return [MatrimonyResponse.model_validate(record) for record in records]

    async def record_matrimony(
        self, data: MatrimonyCreate, created_by_user_id: uuid.UUID | None = None
    ) -> MatrimonyResponse:
        await self._ensure_register_reference_available(
            MatrimonyRecord, data, ("parish_id", "registry_year", "volume_number", "act_number")
        )
        record = await self.repo.create_matrimony(data)
        self._audit_record_created(record, SacramentType.MATRIMONY, created_by_user_id)
        return MatrimonyResponse.model_validate(record)

    async def record_first_communion(
        self, data: FirstCommunionCreate, created_by_user_id: uuid.UUID | None = None
    ) -> FirstCommunionResponse:
        await self._ensure_register_reference_available(
            FirstCommunionRecord, data, ("parish_id", "registry_year", "volume_number", "act_number")
        )
        record = await self.repo.create_first_communion(data)
        self._audit_record_created(record, SacramentType.FIRST_COMMUNION, created_by_user_id)
        return FirstCommunionResponse.model_validate(record)

    async def record_holy_orders(
        self, data: HolyOrdersCreate, created_by_user_id: uuid.UUID | None = None
    ) -> HolyOrdersResponse:
        await self._ensure_register_reference_available(
            HolyOrdersRecord, data, ("parish_id", "register_book", "page_number", "act_number")
        )
        record = await self.repo.create_holy_orders(data)
        self._audit_record_created(record, SacramentType.HOLY_ORDERS, created_by_user_id)
        return HolyOrdersResponse.model_validate(record)

    async def record_religious_profession(
        self, data: ReligiousProfessionCreate, created_by_user_id: uuid.UUID | None = None
    ) -> ReligiousProfessionResponse:
        await self._ensure_register_reference_available(
            ReligiousProfessionRecord,
            data,
            ("parish_id", "register_book", "page_number", "act_number"),
        )
        record = await self.repo.create_religious_profession(data)
        self._audit_record_created(record, SacramentType.RELIGIOUS_PROFESSION, created_by_user_id)
        return ReligiousProfessionResponse.model_validate(record)

    async def record_anointing_of_the_sick(
        self, data: AnointingOfTheSickCreate, created_by_user_id: uuid.UUID | None = None
    ) -> AnointingOfTheSickResponse:
        record = await self.repo.create_anointing_of_the_sick(data)
        self._audit_record_created(record, SacramentType.ANOINTING_OF_THE_SICK, created_by_user_id)
        return AnointingOfTheSickResponse.model_validate(record)

    async def record_christian_funeral(
        self, data: ChristianFuneralCreate, created_by_user_id: uuid.UUID | None = None
    ) -> ChristianFuneralResponse:
        record = await self.repo.create_christian_funeral(data)
        self._audit_record_created(record, SacramentType.CHRISTIAN_FUNERAL, created_by_user_id)
        return ChristianFuneralResponse.model_validate(record)

    async def issue_certificate(
        self, req: CertificateRequest, issued_by_user_id: uuid.UUID
    ) -> CertificateResponse:
        source = await self.repo.get_record_by_type_and_id(
            req.sacrament_type, req.source_record_id
        )
        person_fields = {
            SacramentType.BAPTISM: ("faithful_id",),
            SacramentType.FIRST_COMMUNION: ("faithful_id",),
            SacramentType.CONFIRMATION: ("faithful_id",),
            SacramentType.MATRIMONY: ("groom_faithful_id", "bride_faithful_id"),
            SacramentType.HOLY_ORDERS: ("ordained_faithful_id",),
            SacramentType.RELIGIOUS_PROFESSION: ("professed_faithful_id",),
            SacramentType.ANOINTING_OF_THE_SICK: ("faithful_id",),
            SacramentType.CHRISTIAN_FUNERAL: ("deceased_faithful_id",),
        }
        linked_person = source and any(
            getattr(source, field) == req.faithful_id
            for field in person_fields[req.sacrament_type]
        )
        if (
            not source
            or source.parish_id != req.parish_id
            or not linked_person
        ):
            raise ValidationException(
                "A certificate must refer to a matching sacramental register entry.",
                message_key="errors.sacramental_record_required_for_certificate",
            )
        verification_token = secrets.token_urlsafe(32)
        cert_num = f"CERT-{req.sacrament_type.value[:3]}-{uuid.uuid4().hex[:8].upper()}"
        verification_url = (
            f"{settings.PUBLIC_FRONTEND_URL.rstrip('/')}/verify/{verification_token}"
        )

        issue = CertificateIssue(
            certificate_number=cert_num,
            sacrament_type=req.sacrament_type,
            source_record_id=req.source_record_id,
            faithful_id=req.faithful_id,
            parish_id=req.parish_id,
            issued_by_user_id=issued_by_user_id,
            verification_token=verification_token,
            qr_code_payload=verification_url,
        )
        saved = await self.repo.create_certificate_issue(issue)
        self.db.add(
            AuditLog(
                user_id=issued_by_user_id,
                action="SACRAMENTAL_CERTIFICATE_ISSUED",
                entity_name=req.sacrament_type.value,
                entity_id=str(saved.id),
                details={
                    "certificate_number": saved.certificate_number,
                    "source_record_id": str(req.source_record_id),
                    "faithful_id": str(req.faithful_id),
                    "parish_id": str(req.parish_id),
                },
            )
        )

        return CertificateResponse(
            id=saved.id,
            certificate_number=saved.certificate_number,
            sacrament_type=saved.sacrament_type,
            source_record_id=saved.source_record_id,
            faithful_id=saved.faithful_id,
            parish_id=saved.parish_id,
            verification_token=saved.verification_token,
            qr_code_base64=generate_qr_code_base64(verification_url),
            created_at=saved.created_at,
        )

    async def get_certificate_pdf(self, certificate_id: uuid.UUID) -> tuple[bytes, str]:
        """Render a printable PDF for an issued certificate and return (bytes, filename)."""
        issue = await self.repo.get_certificate_by_id(certificate_id)
        if not issue:
            raise EntityNotFoundException("errors.certificate_not_found")

        faithful = await self.repo.get_faithful_by_id(issue.faithful_id)
        parish = await self.repo.get_parish_by_id(issue.parish_id)

        if faithful:
            recipient = f"{faithful.first_name} {faithful.last_name} ({faithful.christian_name})"
        else:
            recipient = "Registered Faithful"

        details = {
            "Sacrament": issue.sacrament_type.value.replace("_", " ").title(),
            "Parish": parish.name if parish else "",
        }
        if issue.source_record_id:
            source = await self.repo.get_record_by_type_and_id(
                issue.sacrament_type, issue.source_record_id
            )
            if source:
                if hasattr(source, "registry_year"):
                    details["Register reference"] = (
                        f"{source.registry_year} / {source.volume_number} / "
                        f"{source.page_number} / {source.act_number}"
                    )
                elif hasattr(source, "register_book"):
                    details["Register reference"] = (
                        f"{source.register_book} / {source.page_number} / {source.act_number}"
                    )
                for date_field in (
                    "celebration_date", "ordination_date", "profession_date",
                    "anointing_date", "funeral_date",
                ):
                    if hasattr(source, date_field):
                        details["Celebration date"] = getattr(source, date_field).isoformat()
                        break
        title = SACRAMENT_DISPLAY_NAMES.get(issue.sacrament_type, "Sacramental Certificate")
        pdf = generate_certificate_pdf(
            title=title,
            recipient=recipient,
            details=details,
            issued_at=issue.created_at,
            issued_by=settings.APP_NAME,
            certificate_number=issue.certificate_number,
            qr_image_bytes=generate_qr_code_bytes(issue.qr_code_payload),
            verification_url=issue.qr_code_payload,
        )
        return pdf, f"{issue.certificate_number}.pdf"

    async def verify_certificate(self, token: str) -> CertificateVerificationResponse:
        """Validate a certificate's verification token (public QR verification)."""
        issue = await self.repo.get_certificate_by_token(token)
        if not issue:
            raise CertificateInvalidException()
        return CertificateVerificationResponse(
            certificate_number=issue.certificate_number,
            sacrament_type=issue.sacrament_type,
            created_at=issue.created_at,
        )

    # -----------------------------------------------------------------------
    # Sacramental Amendment Workflow
    # -----------------------------------------------------------------------

    async def request_amendment(
        self,
        data: AmendmentRequestCreate,
        requested_by_user_id: uuid.UUID | None = None,
    ) -> SacramentalAmendmentResponse:
        """Submit a formal canonical amendment request for a sacramental record."""
        target_record = await self.repo.get_record_by_type_and_id(
            sacrament_type=data.sacrament_type,
            record_id=data.record_id,
        )
        if not target_record:
            raise EntityNotFoundException(
                "errors.target_record_not_found",
                message_params={
                    "type": data.sacrament_type.value,
                    "record_id": str(data.record_id),
                },
            )

        # Only explicitly approved register fields may be changed. In particular,
        # callers cannot reassign record ownership or alter deletion/audit fields.
        for field_name, change in data.field_changes.items():
            if field_name not in AMENDABLE_FIELDS[data.sacrament_type]:
                raise ValidationException(
                    "errors.field_not_valid",
                    message_params={"field": field_name, "type": data.sacrament_type.value},
                )
            if not isinstance(change, dict) or "old" not in change or "new" not in change:
                raise ValidationException(
                    "errors.amendment_change_requires_old_and_new",
                    message_params={"field": field_name},
                )
            if _canonical_value(getattr(target_record, field_name)) != _canonical_value(
                change["old"]
            ):
                raise ValidationException(
                    "errors.amendment_old_value_mismatch",
                    message_params={"field": field_name},
                )

        amendment = await self.repo.create_amendment(
            data=data,
            requested_by_user_id=requested_by_user_id,
        )

        self.db.add(
            AuditLog(
                user_id=requested_by_user_id,
                action="SACRAMENTAL_AMENDMENT_REQUESTED",
                entity_name=data.sacrament_type.value,
                entity_id=str(data.record_id),
                details={
                    "amendment_id": str(amendment.id),
                    "amendment_type": data.amendment_type.value,
                    "reason": data.reason,
                    "changed_fields": sorted(data.field_changes),
                },
            )
        )
        return SacramentalAmendmentResponse.model_validate(amendment)

    async def list_amendments(
        self,
        sacrament_type: SacramentType | None = None,
        record_id: uuid.UUID | None = None,
        amendment_status: str | None = None,
    ) -> list[SacramentalAmendmentResponse]:
        items = await self.repo.list_amendments(
            sacrament_type=sacrament_type,
            record_id=record_id,
            status=amendment_status,
        )
        return [SacramentalAmendmentResponse.model_validate(a) for a in items]

    async def get_amendment(self, amendment_id: uuid.UUID) -> SacramentalAmendmentResponse:
        amendment = await self.repo.get_amendment_by_id(amendment_id)
        if not amendment:
            raise EntityNotFoundException("errors.sacramental_amendment_not_found")
        return SacramentalAmendmentResponse.model_validate(amendment)

    async def review_amendment(
        self,
        amendment_id: uuid.UUID,
        review: AmendmentReviewRequest,
        reviewer_id: uuid.UUID,
    ) -> SacramentalAmendmentResponse:
        """Approve or reject a sacramental amendment. On approval, safely updates record and appends marginal note."""
        amendment = await self.repo.get_amendment_by_id(amendment_id)
        if not amendment:
            raise EntityNotFoundException("errors.sacramental_amendment_not_found")

        if amendment.status != AmendmentStatus.PENDING:
            raise ValidationException(
                "errors.amendment_not_pending",
                message_params={"status": amendment.status.value},
            )

        now = datetime.now(UTC)

        if review.action == "APPROVE":
            target_record = await self.repo.get_record_by_type_and_id(
                sacrament_type=amendment.sacrament_type,
                record_id=amendment.record_id,
            )
            if not target_record:
                raise EntityNotFoundException("errors.target_amend_record_not_found")

            # Apply field modifications
            for field_name, change_val in amendment.field_changes.items():
                if field_name not in AMENDABLE_FIELDS[amendment.sacrament_type]:
                    raise ValidationException(
                        "errors.field_not_valid",
                        message_params={"field": field_name, "type": amendment.sacrament_type.value},
                    )
                if not isinstance(change_val, dict) or "old" not in change_val or "new" not in change_val:
                    raise ValidationException(
                        "errors.amendment_change_requires_old_and_new",
                        message_params={"field": field_name},
                    )
                current_value = getattr(target_record, field_name)
                if _canonical_value(current_value) != _canonical_value(change_val["old"]):
                    raise ValidationException(
                        "errors.amendment_old_value_mismatch",
                        message_params={"field": field_name},
                    )
                setattr(
                    target_record,
                    field_name,
                    _coerce_amendment_value(current_value, change_val["new"]),
                )

            # Append canonical adnotatio marginalis
            if hasattr(target_record, "marginal_notes"):
                existing_notes = target_record.marginal_notes or ""
                date_str = now.strftime("%Y-%m-%d %H:%M UTC")
                marginal_annotation = (
                    f"\n[Canonical Amendment Approved on {date_str} by {reviewer_id}: "
                    f"{amendment.reason}]"
                )
                target_record.marginal_notes = (existing_notes + marginal_annotation).strip()

            # Record Audit Log
            audit = AuditLog(
                user_id=reviewer_id,
                action="SACRAMENTAL_AMENDMENT_APPROVED",
                entity_name=amendment.sacrament_type.value,
                entity_id=str(amendment.record_id),
                details={
                    "amendment_id": str(amendment.id),
                    "reason": amendment.reason,
                    "changes": amendment.field_changes,
                    "review_notes": review.review_notes,
                },
            )
            self.db.add(audit)

            amendment.status = AmendmentStatus.APPROVED
            amendment.reviewed_by_user_id = reviewer_id
            amendment.reviewed_at = now
            amendment.review_notes = review.review_notes

        elif review.action == "REJECT":
            audit = AuditLog(
                user_id=reviewer_id,
                action="SACRAMENTAL_AMENDMENT_REJECTED",
                entity_name=amendment.sacrament_type.value,
                entity_id=str(amendment.record_id),
                details={
                    "amendment_id": str(amendment.id),
                    "reason": amendment.reason,
                    "review_notes": review.review_notes,
                },
            )
            self.db.add(audit)

            amendment.status = AmendmentStatus.REJECTED
            amendment.reviewed_by_user_id = reviewer_id
            amendment.reviewed_at = now
            amendment.review_notes = review.review_notes

        await self.db.flush()
        return SacramentalAmendmentResponse.model_validate(amendment)
