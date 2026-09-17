"""
Integration tests for the sacramental certificate pipeline:

1. ``POST /sacraments/certificates/issue`` issues a certificate with QR token,
2. ``GET /sacraments/certificates/{id}/pdf`` streams a real, valid PDF file,
3. ``GET /sacraments/certificates/verify/{token}`` validates the QR token (public),
4. the Celery batch task ``certificates.generate_batch`` renders and persists PDFs.

Requires a live Postgres + Redis (mirroring development/production wiring).
"""
import uuid
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.deanery import Archdiocese, Deanery
from app.models.enums import UserRole
from app.models.faithful import Faithful, Gender, CanonicalStatus
from app.models.parish import Parish
from app.models.sacrament import CertificateIssue, SacramentType
from app.models.user import User


@pytest.fixture
async def cert_scenario():
    """Org hierarchy + faithful + secretary user for certificate workflows."""
    created_ids: dict = {"users": [], "faithful": [], "arch_id": None, "dea_id": None, "par_id": None}
    async with AsyncSessionLocal() as db:
        arch = Archdiocese(name=f"Arch {uuid.uuid4().hex[:6]}", see_city="Kigali")
        db.add(arch)
        await db.flush()
        dea = Deanery(archdiocese_id=arch.id, name=f"Deanery {uuid.uuid4().hex[:6]}", code=f"D-{uuid.uuid4().hex[:6]}")
        db.add(dea)
        await db.flush()
        par = Parish(deanery_id=dea.id, name=f"Parish {uuid.uuid4().hex[:6]}", code=f"P-{uuid.uuid4().hex[:6]}")
        db.add(par)
        await db.flush()

        faithful = Faithful(
            registration_number=f"REG-{uuid.uuid4().hex[:8].upper()}",
            first_name="Jean",
            last_name="Baptiste",
            christian_name="Karemera",
            gender=Gender.MALE,
            canonical_status=CanonicalStatus.BAPTIZED,
            parish_id=par.id,
        )
        db.add(faithful)
        await db.flush()

        pwd = f"pass-{uuid.uuid4().hex[:6]}"
        uname = f"sec_{uuid.uuid4().hex[:8]}"
        user = User(
            email=f"{uname}@arkidi.test",
            username=uname,
            hashed_password=get_password_hash(pwd),
            full_name="Secretary Test User",
            role=UserRole.PARISH_SECRETARY,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        await db.commit()

        created_ids["users"].append(user.id)
        created_ids["arch_id"] = arch.id
        created_ids["dea_id"] = dea.id
        created_ids["par_id"] = par.id
        created_ids["faithful"].append(faithful.id)

        creds = {"username": uname, "password": pwd}

    try:
        yield {
            "parish_id": par.id,
            "faithful_id": faithful.id,
            "creds": creds,
        }
    finally:
        async with AsyncSessionLocal() as db:
            for fid in created_ids["faithful"]:
                await db.execute(delete(CertificateIssue).where(CertificateIssue.faithful_id == fid))
            for uid in created_ids["users"]:
                await db.execute(delete(User).where(User.id == uid))
            for fid in created_ids["faithful"]:
                await db.execute(delete(Faithful).where(Faithful.id == fid))
            if created_ids["par_id"]:
                await db.execute(delete(Parish).where(Parish.id == created_ids["par_id"]))
            if created_ids["dea_id"]:
                await db.execute(delete(Deanery).where(Deanery.id == created_ids["dea_id"]))
            if created_ids["arch_id"]:
                await db.execute(delete(Archdiocese).where(Archdiocese.id == created_ids["arch_id"]))
            await db.commit()


async def _headers(client: AsyncClient, creds: dict) -> dict:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": creds["username"], "password": creds["password"]},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
@pytest.mark.asyncio
async def test_certificate_issue_download_verify(client: AsyncClient, cert_scenario):
    data = cert_scenario
    headers = await _headers(client, data["creds"])

    # 1. Issue a certificate with QR verification payload
    issue = await client.post(
        "/api/v1/sacraments/certificates/issue",
        json={
            "sacrament_type": SacramentType.BAPTISM.value,
            "faithful_id": str(data["faithful_id"]),
            "parish_id": str(data["parish_id"]),
        },
        headers=headers,
    )
    assert issue.status_code == 201, issue.text
    issue_data = issue.json()["data"]
    cert_id = issue_data["id"]
    token = issue_data["verification_token"]
    assert issue_data["qr_code_base64"].startswith("data:image/png;base64,")

    # 2. Download a real, non-trivial PDF
    pdf = await client.get(f"/api/v1/sacraments/certificates/{cert_id}/pdf", headers=headers)
    assert pdf.status_code == 200, pdf.text
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:5] == b"%PDF-"
    assert "attachment" in pdf.headers.get("content-disposition", "")
    assert len(pdf.content) > 5000

    # 3. Public QR verification succeeds
    verify = await client.get(f"/api/v1/sacraments/certificates/verify/{token}")
    assert verify.status_code == 200, verify.text
    verify_data = verify.json()["data"]
    assert verify_data["certificate_number"] == issue_data["certificate_number"]
    assert verify_data["sacrament_type"] == SacramentType.BAPTISM.value

    # 4. Invalid/unknown token is rejected
    bad = await client.get("/api/v1/sacraments/certificates/verify/not-a-real-token")
    assert bad.status_code == 400


@pytest.mark.asyncio
async def test_certificate_batch_task(client: AsyncClient, cert_scenario, tmp_path):
    from app.config import settings
    from app.tasks.certificates import render_certificate_batch

    data = cert_scenario
    headers = await _headers(client, data["creds"])
    issue = await client.post(
        "/api/v1/sacraments/certificates/issue",
        json={
            "sacrament_type": SacramentType.BAPTISM.value,
            "faithful_id": str(data["faithful_id"]),
            "parish_id": str(data["parish_id"]),
        },
        headers=headers,
    )
    assert issue.status_code == 201
    cert_id = issue.json()["data"]["id"]

    original_dir = settings.FILE_STORAGE_PATH
    settings.FILE_STORAGE_PATH = str(tmp_path)
    try:
        result = await render_certificate_batch([str(cert_id)])
        assert result["generated"] == 1, result
        assert result["failed"] == []

        out_dir = Path(result["output_directory"])
        files = list(out_dir.glob("*.pdf"))
        assert len(files) == 1
        assert files[0].read_bytes()[:5] == b"%PDF-"
    finally:
        settings.FILE_STORAGE_PATH = original_dir