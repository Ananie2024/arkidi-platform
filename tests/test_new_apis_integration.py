"""
Integration tests for new API surfaces:
1. Survey API (Survey, SurveyQuestion, SurveyResponse, aggregation)
2. Document API (DocumentType, Document scoping & metadata)
3. Governance API (Commission, Council, Meeting, MeetingMinute)
4. Sacramental Amendment Workflow (request, review, marginal notes, audit logs)
"""
import uuid
from datetime import date
import pytest
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.deanery import Archdiocese, Deanery
from app.models.enums import UserRole
from app.models.faithful import Faithful
from app.models.parish import Parish
from app.models.sacrament import BaptismRecord, SacramentType, SacramentalAmendment
from app.models.survey import Survey, SurveyResponse
from app.models.document import Document
from app.models.document_type import DocumentType
from app.models.commission import Commission
from app.models.council import Council
from app.models.meeting import Meeting
from app.models.meeting_minute import MeetingMinute
from app.models.user import User


@pytest.fixture
async def auth_users():
    """Create test users for different roles and return token headers."""
    created_ids = []
    headers_by_role = {}

    roles = [
        (UserRole.SUPER_ADMIN, "admin_user"),
        (UserRole.CHANCELLOR, "chancellor_user"),
        (UserRole.PARISH_PRIEST, "priest_user"),
        (UserRole.PARISH_SECRETARY, "secretary_user"),
        (UserRole.READ_ONLY_AUDITOR, "auditor_user"),
    ]

    async with AsyncSessionLocal() as db:
        for role, prefix in roles:
            uname = f"{prefix}_{uuid.uuid4().hex[:6]}"
            pwd = f"pass-{uname}"
            user = User(
                email=f"{uname}@arkidi.test",
                username=uname,
                hashed_password=get_password_hash(pwd),
                full_name=f"Test {role.value}",
                role=role,
                is_active=True,
            )
            db.add(user)
            await db.flush()
            created_ids.append(user.id)
            headers_by_role[role] = (uname, pwd, user.id)
        await db.commit()

    async def get_headers(client: AsyncClient, role: UserRole) -> dict:
        uname, pwd, _ = headers_by_role[role]
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": uname, "password": pwd},
        )
        assert resp.status_code == 200, resp.text
        token = resp.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    yield get_headers

    async with AsyncSessionLocal() as db:
        for uid in created_ids:
            await db.execute(delete(User).where(User.id == uid))
        await db.commit()


@pytest.fixture
async def geo_setup():
    """Create Archdiocese, Deanery, Parish for test scoping."""
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
        await db.commit()
        yield arch.id, dea.id, par.id

        await db.execute(delete(Parish).where(Parish.id == par.id))
        await db.execute(delete(Deanery).where(Deanery.id == dea.id))
        await db.execute(delete(Archdiocese).where(Archdiocese.id == arch.id))
        await db.commit()


# ---------------------------------------------------------------------------
# 1. Survey API Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_survey_lifecycle_and_responses(client: AsyncClient, auth_users, geo_setup):
    arch_id, dea_id, par_id = geo_setup
    priest_headers = await auth_users(client, UserRole.PARISH_PRIEST)
    secretary_headers = await auth_users(client, UserRole.PARISH_SECRETARY)
    auditor_headers = await auth_users(client, UserRole.READ_ONLY_AUDITOR)

    # 1. Create survey with question schema (Draft)
    survey_payload = {
        "title": "2026 Synodality & Pastoral Needs Survey",
        "description": "Annual pastoral survey for parish communities",
        "status": "DRAFT",
        "parish_id": str(par_id),
        "questions": [
            {
                "id": "q1",
                "question_text": "How many years have you been part of this parish?",
                "question_type": "NUMBER",
                "required": True,
            },
            {
                "id": "q2",
                "question_text": "Which pastoral priority is most urgent?",
                "question_type": "SINGLE_CHOICE",
                "options": ["Youth", "Catechesis", "Caritas", "Family"],
                "required": True,
            },
        ],
    }

    create_resp = await client.post("/api/v1/surveys", json=survey_payload, headers=priest_headers)
    assert create_resp.status_code == 201, create_resp.text
    survey_data = create_resp.json()["data"]
    survey_id = survey_data["id"]
    assert survey_data["title"] == survey_payload["title"]
    assert len(survey_data["questions"]) == 2

    # 2. Cannot answer while DRAFT
    ans_payload = {
        "respondent_name": "Jean Baptiste",
        "respondent_parish_id": str(par_id),
        "answers": {"q1": 5, "q2": "Youth"},
    }
    draft_submit = await client.post(f"/api/v1/surveys/{survey_id}/responses", json=ans_payload, headers=secretary_headers)
    assert draft_submit.status_code == 400

    # 3. Activate survey
    update_resp = await client.put(f"/api/v1/surveys/{survey_id}", json={"status": "ACTIVE"}, headers=priest_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["status"] == "ACTIVE"

    # 4. Submit valid responses
    resp1 = await client.post(f"/api/v1/surveys/{survey_id}/responses", json=ans_payload, headers=secretary_headers)
    assert resp1.status_code == 201, resp1.text
    ans_id1 = resp1.json()["data"]["id"]

    ans_payload2 = {
        "respondent_name": "Marie Claire",
        "respondent_parish_id": str(par_id),
        "answers": {"q1": 15, "q2": "Youth"},
    }
    resp2 = await client.post(f"/api/v1/surveys/{survey_id}/responses", json=ans_payload2, headers=secretary_headers)
    assert resp2.status_code == 201

    # 5. List responses
    list_resp = await client.get(f"/api/v1/surveys/{survey_id}/responses", headers=auditor_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) == 2

    # 6. Check summary analytics
    summary_resp = await client.get(f"/api/v1/surveys/{survey_id}/summary", headers=auditor_headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()["data"]
    assert summary["total_responses"] == 2
    assert summary["question_summaries"]["q1"]["average"] == 10.0
    assert summary["question_summaries"]["q2"]["frequencies"]["Youth"] == 2

    # Cleanup survey
    async with AsyncSessionLocal() as db:
        await db.execute(delete(SurveyResponse).where(SurveyResponse.survey_id == uuid.UUID(survey_id)))
        await db.execute(delete(Survey).where(Survey.id == uuid.UUID(survey_id)))
        await db.commit()


# ---------------------------------------------------------------------------
# 2. Generic Document API Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_document_and_type_lifecycle(client: AsyncClient, auth_users, geo_setup):
    _, _, par_id = geo_setup
    admin_headers = await auth_users(client, UserRole.SUPER_ADMIN)
    secretary_headers = await auth_users(client, UserRole.PARISH_SECRETARY)
    auditor_headers = await auth_users(client, UserRole.READ_ONLY_AUDITOR)

    # 1. Create DocumentType
    type_code = f"DECREE_{uuid.uuid4().hex[:6]}"
    doc_type_payload = {
        "code": type_code,
        "name_en": "Official Canonical Decree",
        "name_fr": "Décret canonique officiel",
        "name_rw": "Iteka ry'ubuyobozi bwa Kiliziya",
        "category": "CANONICAL",
    }
    create_type_resp = await client.post("/api/v1/documents/types", json=doc_type_payload, headers=admin_headers)
    assert create_type_resp.status_code == 201, create_type_resp.text
    type_id = create_type_resp.json()["data"]["id"]

    # 2. Create Document with parish scope
    doc_payload = {
        "title": "Parish Erection Decree",
        "document_type_id": type_id,
        "classification": "ARCHIVE",
        "parish_id": str(par_id),
        "file_path": "documents/2026/erection_decree.pdf",
        "file_size_bytes": 102400,
        "mime_type": "application/pdf",
        "checksum_sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    }
    create_doc_resp = await client.post("/api/v1/documents", json=doc_payload, headers=secretary_headers)
    assert create_doc_resp.status_code == 201, create_doc_resp.text
    doc_data = create_doc_resp.json()["data"]
    doc_id = doc_data["id"]
    assert doc_data["title"] == "Parish Erection Decree"
    assert doc_data["parish_id"] == str(par_id)

    # 3. Validation: Document without any scoping FK should be rejected
    invalid_doc = {
        "title": "Unscoped Document",
        "document_type_id": type_id,
        "file_path": "documents/invalid.pdf",
    }
    inv_resp = await client.post("/api/v1/documents", json=invalid_doc, headers=secretary_headers)
    assert inv_resp.status_code == 422

    # 4. List documents filtered by parish_id
    list_docs = await client.get(f"/api/v1/documents?parish_id={par_id}", headers=auditor_headers)
    assert list_docs.status_code == 200
    docs = list_docs.json()["data"]
    assert any(d["id"] == doc_id for d in docs)

    # Cleanup
    async with AsyncSessionLocal() as db:
        await db.execute(delete(Document).where(Document.id == uuid.UUID(doc_id)))
        await db.execute(delete(DocumentType).where(DocumentType.id == uuid.UUID(type_id)))
        await db.commit()


# ---------------------------------------------------------------------------
# 3. Governance API Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_governance_layer_crud(client: AsyncClient, auth_users, geo_setup):
    _, _, par_id = geo_setup
    priest_headers = await auth_users(client, UserRole.PARISH_PRIEST)
    secretary_headers = await auth_users(client, UserRole.PARISH_SECRETARY)
    auditor_headers = await auth_users(client, UserRole.READ_ONLY_AUDITOR)

    # 1. Create Commission
    comm_resp = await client.post(
        "/api/v1/governance/commissions",
        json={
            "name": "Commission Pastorale de la Famille",
            "category": "FAMILY",
            "parish_id": str(par_id),
            "leader_name": "Dr. Emmanuel",
        },
        headers=priest_headers,
    )
    assert comm_resp.status_code == 201, comm_resp.text
    comm_id = comm_resp.json()["data"]["id"]

    # 2. Create Council
    council_resp = await client.post(
        "/api/v1/governance/councils",
        json={
            "name": "Conseil Pastoral Paroissial",
            "council_type": "PARISH_PASTORAL",
            "parish_id": str(par_id),
            "president_name": "Père Curé",
        },
        headers=priest_headers,
    )
    assert council_resp.status_code == 201, council_resp.text
    council_id = council_resp.json()["data"]["id"]

    # 3. Create Meeting
    meeting_resp = await client.post(
        "/api/v1/governance/meetings",
        json={
            "title": "Q1 Pastoral Council Meeting",
            "meeting_date": "2026-03-15",
            "venue": "Parish Hall",
            "council_id": council_id,
            "agenda": "Review of Easter preparations",
        },
        headers=secretary_headers,
    )
    assert meeting_resp.status_code == 201, meeting_resp.text
    meeting_id = meeting_resp.json()["data"]["id"]

    # 4. Attach Meeting Minute
    minute_resp = await client.post(
        f"/api/v1/governance/meetings/{meeting_id}/minutes",
        json={
            "title": "Approved Decisions for Easter 2026",
            "content": "Council approved the schedule for Holy Week celebrations.",
        },
        headers=secretary_headers,
    )
    assert minute_resp.status_code == 201, minute_resp.text
    minute_id = minute_resp.json()["data"]["id"]

    # 5. List minutes
    min_list = await client.get(f"/api/v1/governance/meetings/{meeting_id}/minutes", headers=auditor_headers)
    assert min_list.status_code == 200
    assert len(min_list.json()["data"]) == 1

    # Cleanup
    async with AsyncSessionLocal() as db:
        await db.execute(delete(MeetingMinute).where(MeetingMinute.id == uuid.UUID(minute_id)))
        await db.execute(delete(Meeting).where(Meeting.id == uuid.UUID(meeting_id)))
        await db.execute(delete(Council).where(Council.id == uuid.UUID(council_id)))
        await db.execute(delete(Commission).where(Commission.id == uuid.UUID(comm_id)))
        await db.commit()


# ---------------------------------------------------------------------------
# 4. Sacramental Amendment Workflow Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sacramental_amendment_workflow(client: AsyncClient, auth_users, geo_setup):
    _, _, par_id = geo_setup
    secretary_headers = await auth_users(client, UserRole.PARISH_SECRETARY)
    chancellor_headers = await auth_users(client, UserRole.CHANCELLOR)
    auditor_headers = await auth_users(client, UserRole.READ_ONLY_AUDITOR)

    # 1. Create Faithful and Baptism Record
    faithful_id = None
    baptism_id = None
    async with AsyncSessionLocal() as db:
        f = Faithful(
            parish_id=par_id,
            registration_number=f"REG-{uuid.uuid4().hex[:10]}",
            first_name="Jean",
            last_name="Mugisha",
            christian_name="Jean",
            gender="MALE",
            date_of_birth=date(2000, 1, 1),
        )
        db.add(f)
        await db.flush()
        faithful_id = f.id

        b = BaptismRecord(
            parish_id=par_id,
            faithful_id=faithful_id,
            registry_year=2000,
            volume_number="Vol 1",
            page_number="12",
            act_number="045",
            celebration_date=date(2000, 2, 2),
            minister_name="Abbé Jean",
            godfather_name="Pierre Nkurunziza",
        )
        db.add(b)
        await db.flush()
        baptism_id = b.id
        await db.commit()

    amendment_id = None
    try:
        # 2. Secretary requests amendment to correct minister name and godfather
        amend_req = {
            "sacrament_type": "BAPTISM",
            "record_id": str(baptism_id),
            "amendment_type": "CLERICAL_ERROR",
            "reason": "Rectification of minister full canonical name per diocesan directory",
            "field_changes": {
                "minister_name": {"old": "Abbé Jean", "new": "Abbé Jean-Baptiste Gasana"}
            },
        }
        req_resp = await client.post("/api/v1/sacraments/amendments", json=amend_req, headers=secretary_headers)
        assert req_resp.status_code == 201, req_resp.text
        amend_data = req_resp.json()["data"]
        amendment_id = amend_data["id"]
        assert amend_data["status"] == "PENDING"

        # 3. Chancellor approves amendment
        review_resp = await client.post(
            f"/api/v1/sacraments/amendments/{amendment_id}/review",
            json={"action": "APPROVE", "review_notes": "Verified against diocesan archives"},
            headers=chancellor_headers,
        )
        assert review_resp.status_code == 200, review_resp.text
        reviewed_data = review_resp.json()["data"]
        assert reviewed_data["status"] == "APPROVED"

        # 4. Verify target baptism record was amended and marginal note was added
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            stmt = select(BaptismRecord).where(BaptismRecord.id == baptism_id)
            res = await db.execute(stmt)
            updated_baptism = res.scalar_one()
            assert updated_baptism.minister_name == "Abbé Jean-Baptiste Gasana"
            assert "Canonical Amendment Approved" in (updated_baptism.marginal_notes or "")
            assert "Rectification of minister full canonical name" in updated_baptism.marginal_notes
    finally:
        async with AsyncSessionLocal() as db:
            if amendment_id:
                await db.execute(delete(SacramentalAmendment).where(SacramentalAmendment.id == uuid.UUID(amendment_id)))
            if baptism_id:
                await db.execute(delete(BaptismRecord).where(BaptismRecord.id == baptism_id))
            if faithful_id:
                await db.execute(delete(Faithful).where(Faithful.id == faithful_id))
            await db.commit()
