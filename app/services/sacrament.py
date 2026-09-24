"""
Sacraments Module Business Logic Service
"""

import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    CertificateInvalidException,
    EntityNotFoundException,
    ValidationException,
)
from app.models.audit_log import AuditLog
from app.models.sacrament import AmendmentStatus, CertificateIssue, SacramentType
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


class SacramentsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SacramentsRepository(db)

    async def list_baptisms(self, parish_id: uuid.UUID | None = None) -> list[BaptismResponse]:
        records = await self.repo.list_baptisms(parish_id=parish_id)
        return [BaptismResponse.model_validate(record) for record in records]

    async def record_baptism(self, data: BaptismCreate) -> BaptismResponse:
        record = await self.repo.create_baptism(data)
        return BaptismResponse.model_validate(record)

    async def list_confirmations(
        self, parish_id: uuid.UUID | None = None
    ) -> list[ConfirmationResponse]:
        records = await self.repo.list_confirmations(parish_id=parish_id)
        return [ConfirmationResponse.model_validate(record) for record in records]

    async def record_confirmation(self, data: ConfirmationCreate) -> ConfirmationResponse:
        record = await self.repo.create_confirmation(data)
        return ConfirmationResponse.model_validate(record)

    async def list_matrimonies(self, parish_id: uuid.UUID | None = None) -> list[MatrimonyResponse]:
        records = await self.repo.list_matrimonies(parish_id=parish_id)
        return [MatrimonyResponse.model_validate(record) for record in records]

    async def record_matrimony(self, data: MatrimonyCreate) -> MatrimonyResponse:
        record = await self.repo.create_matrimony(data)
        return MatrimonyResponse.model_validate(record)

    async def record_first_communion(self, data: FirstCommunionCreate) -> FirstCommunionResponse:
        record = await self.repo.create_first_communion(data)
        return FirstCommunionResponse.model_validate(record)

    async def record_holy_orders(self, data: HolyOrdersCreate) -> HolyOrdersResponse:
        record = await self.repo.create_holy_orders(data)
        return HolyOrdersResponse.model_validate(record)

    async def record_religious_profession(
        self, data: ReligiousProfessionCreate
    ) -> ReligiousProfessionResponse:
        record = await self.repo.create_religious_profession(data)
        return ReligiousProfessionResponse.model_validate(record)

    async def record_anointing_of_the_sick(
        self, data: AnointingOfTheSickCreate
    ) -> AnointingOfTheSickResponse:
        record = await self.repo.create_anointing_of_the_sick(data)
        return AnointingOfTheSickResponse.model_validate(record)

    async def record_christian_funeral(
        self, data: ChristianFuneralCreate
    ) -> ChristianFuneralResponse:
        record = await self.repo.create_christian_funeral(data)
        return ChristianFuneralResponse.model_validate(record)

    async def issue_certificate(
        self, req: CertificateRequest, issued_by_user_id: uuid.UUID
    ) -> CertificateResponse:
        verification_token = secrets.token_urlsafe(32)
        cert_num = f"CERT-{req.sacrament_type.value[:3]}-{uuid.uuid4().hex[:8].upper()}"
        verification_url = f"https://arkidi.archidiocesekigali.org/verify/{verification_token}"

        issue = CertificateIssue(
            certificate_number=cert_num,
            sacrament_type=req.sacrament_type,
            faithful_id=req.faithful_id,
            parish_id=req.parish_id,
            issued_by_user_id=issued_by_user_id,
            verification_token=verification_token,
            qr_code_payload=verification_url,
        )
        saved = await self.repo.create_certificate_issue(issue)

        return CertificateResponse(
            id=saved.id,
            certificate_number=saved.certificate_number,
            sacrament_type=saved.sacrament_type,
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

    async def verify_certificate(self, token: str) -> CertificateResponse:
        """Validate a certificate's verification token (public QR verification)."""
        issue = await self.repo.get_certificate_by_token(token)
        if not issue:
            raise CertificateInvalidException()
        return CertificateResponse(
            id=issue.id,
            certificate_number=issue.certificate_number,
            sacrament_type=issue.sacrament_type,
            faithful_id=issue.faithful_id,
            parish_id=issue.parish_id,
            verification_token=issue.verification_token,
            qr_code_base64=generate_qr_code_base64(issue.qr_code_payload),
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

        # Validate that requested fields exist on target record
        for field_name in data.field_changes.keys():
            if not hasattr(target_record, field_name):
                raise ValidationException(
                    "errors.field_not_valid",
                    message_params={"field": field_name, "type": data.sacrament_type.value},
                )

        amendment = await self.repo.create_amendment(
            data=data,
            requested_by_user_id=requested_by_user_id,
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
                new_val = change_val.get("new") if isinstance(change_val, dict) else change_val
                if hasattr(target_record, field_name):
                    setattr(target_record, field_name, new_val)

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
