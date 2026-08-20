"""
Sacraments Module Business Logic Service
"""
import uuid
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.sacrament import SacramentsRepository
from app.schemas.sacrament import (
    BaptismCreate,
    BaptismResponse,
    ConfirmationCreate,
    ConfirmationResponse,
    MatrimonyCreate,
    MatrimonyResponse,
    FirstCommunionCreate,
    FirstCommunionResponse,
    HolyOrdersCreate,
    HolyOrdersResponse,
    ReligiousProfessionCreate,
    ReligiousProfessionResponse,
    AnointingOfTheSickCreate,
    AnointingOfTheSickResponse,
    ChristianFuneralCreate,
    ChristianFuneralResponse,
    CertificateRequest,
    CertificateResponse,
)
from app.models.sacrament import CertificateIssue
from app.core.exceptions import SacramentRecordNotFoundException
from app.utils.qr import generate_qr_code_base64


class SacramentsService:
    def __init__(self, db: AsyncSession):
        self.repo = SacramentsRepository(db)

    async def record_baptism(self, data: BaptismCreate) -> BaptismResponse:
        record = await self.repo.create_baptism(data)
        return BaptismResponse.model_validate(record)

    async def record_confirmation(self, data: ConfirmationCreate) -> ConfirmationResponse:
        record = await self.repo.create_confirmation(data)
        return ConfirmationResponse.model_validate(record)

    async def record_matrimony(self, data: MatrimonyCreate) -> MatrimonyResponse:
        record = await self.repo.create_matrimony(data)
        return MatrimonyResponse.model_validate(record)

    async def record_first_communion(self, data: FirstCommunionCreate) -> FirstCommunionResponse:
        record = await self.repo.create_first_communion(data)
        return FirstCommunionResponse.model_validate(record)

    async def record_holy_orders(self, data: HolyOrdersCreate) -> HolyOrdersResponse:
        record = await self.repo.create_holy_orders(data)
        return HolyOrdersResponse.model_validate(record)

    async def record_religious_profession(self, data: ReligiousProfessionCreate) -> ReligiousProfessionResponse:
        record = await self.repo.create_religious_profession(data)
        return ReligiousProfessionResponse.model_validate(record)

    async def record_anointing_of_the_sick(self, data: AnointingOfTheSickCreate) -> AnointingOfTheSickResponse:
        record = await self.repo.create_anointing_of_the_sick(data)
        return AnointingOfTheSickResponse.model_validate(record)

    async def record_christian_funeral(self, data: ChristianFuneralCreate) -> ChristianFuneralResponse:
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
