"""Integration tests for the least-tested backend route surfaces:

1. Governance API — update/delete flows, 404s and role enforcement for
   Commission / Council / Meeting / MeetingMinute (CRUD-create happy paths
   are covered by tests/test_new_apis_integration.py).
2. Finance API — donation recording, listing and the typed financial summary.
3. Liturgy API — mass schedules and mass intentions.
4. Archives indicators end-to-end — documents_by_type through the generic
   /statistics/indicators pipeline (ADR 002 follow-up).

Needs live Postgres + Redis, same as the other integration tests.
"""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.commission import Commission
from app.models.council import Council
from app.models.deanery import Archdiocese, Deanery
from app.models.document import Document
from app.models.document_type import DocumentType
from app.models.donation import Donation
from app.models.enums import UserRole
from app.models.intention import MassIntention
from app.models.mass import MassSchedule
from app.models.meeting import Meeting
from app.models.meeting_minute import MeetingMinute
from app.models.parish import Parish
from app.models.user import User


@pytest.fixture
async def auth_users():
    """Create one active user per role; return a header-resolution helper."""
    created_ids = []
    creds_by_role = {}

    roles = [
        UserRole.SUPER_ADMIN,
        UserRole.CHANCELLOR,
        UserRole.PARISH_PRIEST,
        UserRole.PARISH_VICAR,
        UserRole.PARISH_SECRETARY,
        UserRole.MINISTRY_LEADER,
        UserRole.READ_ONLY_AUDITOR,
    ]

    async with AsyncSessionLocal() as db:
        for role in roles:
            uname = f"routes_{role.value.lower()}_{uuid.uuid4().hex[:6]}"
            pwd = f"pass-{uuid.uuid4().hex[:8]}"
            user = User(
                email=f"{uname}@arkidi.test",
                username=uname,
                hashed_password=get_password_hash(pwd),
                full_name=f"Routes {role.value}",
                role=role,
                is_active=True,
            )
            db.add(user)
            await db.flush()
            created_ids.append(user.id)
            creds_by_role[role] = (uname, pwd)
        await db.commit()

    async def get_headers(client: AsyncClient, role: UserRole) -> dict:
        uname, pwd = creds_by_role[role]
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": uname, "password": pwd},
        )
        assert resp.status_code == 200, resp.text
        return {"Authorization": f"Bearer {resp.json()['data']['access_token']}"}

    yield get_headers

    async with AsyncSessionLocal() as db:
        for uid in created_ids:
            await db.execute(delete(User).where(User.id == uid))
        await db.commit()


@pytest.fixture
async def geo_setup():
    """Archdiocese -> Deanery -> Parish, cleaned up afterwards."""
    async with AsyncSessionLocal() as db:
        arch = Archdiocese(name=f"Routes Arch {uuid.uuid4().hex[:6]}", see_city="Kigali")
        db.add(arch)
        await db.flush()
        dea = Deanery(
            archdiocese_id=arch.id,
            name=f"Routes Deanery {uuid.uuid4().hex[:6]}",
            code=f"DOY-{uuid.uuid4().hex[:8]}",
        )
        db.add(dea)
        await db.flush()
        par = Parish(
            deanery_id=dea.id,
            name=f"Routes Parish {uuid.uuid4().hex[:6]}",
            code=f"PAR-{uuid.uuid4().hex[:8]}",
        )
        db.add(par)
        await db.flush()
        await db.commit()
        yield arch.id, dea.id, par.id

        await db.execute(delete(Parish).where(Parish.id == par.id))
        await db.execute(delete(Deanery).where(Deanery.id == dea.id))
        await db.execute(delete(Archdiocese).where(Archdiocese.id == arch.id))
        await db.commit()


# ---------------------------------------------------------------------------
# 1. Governance API — update/delete, 404s, role enforcement
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_governance_update_delete_and_404s(client: AsyncClient, auth_users, geo_setup):
    _, _, par_id = geo_setup
    priest_headers = await auth_users(client, UserRole.PARISH_PRIEST)
    secretary_headers = await auth_users(client, UserRole.PARISH_SECRETARY)
    auditor_headers = await auth_users(client, UserRole.READ_ONLY_AUDITOR)

    # Seed the full chain.
    comm = await client.post(
        "/api/v1/governance/commissions",
        json={"name": "Commission de la Famille", "category": "FAMILY", "parish_id": str(par_id)},
        headers=priest_headers,
    )
    assert comm.status_code == 201, comm.text
    comm_id = comm.json()["data"]["id"]

    council = await client.post(
        "/api/v1/governance/councils",
        json={"name": "Conseil Pastoral Paroissial", "council_type": "PARISH_PASTORAL", "parish_id": str(par_id)},
        headers=priest_headers,
    )
    assert council.status_code == 201, council.text
    council_id = council.json()["data"]["id"]

    meeting = await client.post(
        "/api/v1/governance/meetings",
        json={
            "title": "Q2 Council Meeting",
            "meeting_date": "2026-06-10",
            "venue": "Parish Hall",
            "council_id": council_id,
        },
        headers=secretary_headers,
    )
    assert meeting.status_code == 201, meeting.text
    meeting_id = meeting.json()["data"]["id"]

    minute = await client.post(
        f"/api/v1/governance/meetings/{meeting_id}/minutes",
        json={"title": "Q2 Decisions", "content": "Initial draft."},
        headers=secretary_headers,
    )
    assert minute.status_code == 201, minute.text
    minute_id = minute.json()["data"]["id"]

    try:
        # --- Updates -----------------------------------------------------
        upd_comm = await client.put(
            f"/api/v1/governance/commissions/{comm_id}",
            json={"leader_name": "Dr. Emmanuel"},
            headers=priest_headers,
        )
        assert upd_comm.status_code == 200, upd_comm.text
        assert upd_comm.json()["data"]["leader_name"] == "Dr. Emmanuel"

        upd_council = await client.put(
            f"/api/v1/governance/councils/{council_id}",
            json={"president_name": "Père Curé"},
            headers=priest_headers,
        )
        assert upd_council.status_code == 200, upd_council.text
        assert upd_council.json()["data"]["president_name"] == "Père Curé"

        upd_meeting = await client.put(
            f"/api/v1/governance/meetings/{meeting_id}",
            json={"decisions": "Easter plan approved", "status": "HELD"},
            headers=secretary_headers,
        )
        assert upd_meeting.status_code == 200, upd_meeting.text
        assert upd_meeting.json()["data"]["status"] == "HELD"

        upd_minute = await client.put(
            f"/api/v1/governance/minutes/{minute_id}",
            json={"content": "Final approved decisions."},
            headers=secretary_headers,
        )
        assert upd_minute.status_code == 200, upd_minute.text
        assert upd_minute.json()["data"]["content"] == "Final approved decisions."

        # Single reads work for the auditor.
        got_minute = await client.get(f"/api/v1/governance/minutes/{minute_id}", headers=auditor_headers)
        assert got_minute.status_code == 200, got_minute.text

        # --- 404s ---------------------------------------------------------
        for url in (
            f"/api/v1/governance/commissions/{uuid.uuid4()}",
            f"/api/v1/governance/councils/{uuid.uuid4()}",
            f"/api/v1/governance/meetings/{uuid.uuid4()}",
            f"/api/v1/governance/minutes/{uuid.uuid4()}",
        ):
            resp = await client.get(url, headers=auditor_headers)
            assert resp.status_code == 404, f"{url}: {resp.text}"
    finally:
        # --- Deletes (drive the soft-delete paths) ------------------------
        del_minute = await client.delete(f"/api/v1/governance/minutes/{minute_id}", headers=secretary_headers)
        assert del_minute.status_code == 200, del_minute.text
        del_meeting = await client.delete(f"/api/v1/governance/meetings/{meeting_id}", headers=secretary_headers)
        assert del_meeting.status_code == 200, del_meeting.text
        del_council = await client.delete(f"/api/v1/governance/councils/{council_id}", headers=priest_headers)
        assert del_council.status_code == 200, del_council.text
        del_comm = await client.delete(f"/api/v1/governance/commissions/{comm_id}", headers=priest_headers)
        assert del_comm.status_code == 200, del_comm.text

        # Deleted minute is no longer readable.
        gone = await client.get(f"/api/v1/governance/minutes/{minute_id}", headers=auditor_headers)
        assert gone.status_code == 404, gone.text

        # The API soft-deletes; hard-remove the rows so the geo_setup parish
        # teardown does not trip the commissions/councils FK constraints.
        async with AsyncSessionLocal() as db:
            await db.execute(delete(MeetingMinute).where(MeetingMinute.id == uuid.UUID(minute_id)))
            await db.execute(delete(Meeting).where(Meeting.id == uuid.UUID(meeting_id)))
            await db.execute(delete(Council).where(Council.id == uuid.UUID(council_id)))
            await db.execute(delete(Commission).where(Commission.id == uuid.UUID(comm_id)))
            await db.commit()


@pytest.mark.asyncio
async def test_governance_role_enforcement(client: AsyncClient, auth_users, geo_setup):
    _, _, par_id = geo_setup
    secretary_headers = await auth_users(client, UserRole.PARISH_SECRETARY)
    auditor_headers = await auth_users(client, UserRole.READ_ONLY_AUDITOR)

    # A parish secretary is not allowed to create commissions (403).
    forbidden = await client.post(
        "/api/v1/governance/commissions",
        json={"name": "Commission Clandestine", "parish_id": str(par_id)},
        headers=secretary_headers,
    )
    assert forbidden.status_code == 403, forbidden.text

    # Unauthenticated requests are rejected outright (401).
    anon = await client.get("/api/v1/governance/commissions")
    assert anon.status_code == 401, anon.text

    # The read-only auditor can list but not create.
    listing = await client.get("/api/v1/governance/commissions", headers=auditor_headers)
    assert listing.status_code == 200, listing.text

    auditor_create = await client.post(
        "/api/v1/governance/commissions",
        json={"name": "Commission Audit", "parish_id": str(par_id)},
        headers=auditor_headers,
    )
    assert auditor_create.status_code == 403, auditor_create.text


# ---------------------------------------------------------------------------
# 2. Finance API — donations, listing, typed summary
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_finance_donation_lifecycle_and_summary(client: AsyncClient, auth_users, geo_setup):
    _, _, par_id = geo_setup
    secretary_headers = await auth_users(client, UserRole.PARISH_SECRETARY)
    leader_headers = await auth_users(client, UserRole.MINISTRY_LEADER)
    auditor_headers = await auth_users(client, UserRole.READ_ONLY_AUDITOR)

    donation_ids = []
    try:
        # Secretary records donations of the three summarised types.
        for donation_type, amount in (
            ("TITHE", 10000),
            ("OFFERTORY", 5000),
            ("CONSTRUCTION_FUND", 25000),
        ):
            resp = await client.post(
                "/api/v1/finance/donations",
                json={
                    "parish_id": str(par_id),
                    "donation_type": donation_type,
                    "amount": amount,
                    "donation_date": "2026-05-04",
                },
                headers=secretary_headers,
            )
            assert resp.status_code == 201, resp.text
            data = resp.json()["data"]
            donation_ids.append(data["id"])
            assert data["receipt_number"], "receipt number must be generated"

        # MINISTRY_LEADER has no financial create permission (403).
        # (PARISH_PRIEST, by contrast, inherits PARISH_SECRETARY in the RBAC
        # hierarchy, so a priest IS allowed to record donations.)
        denied = await client.post(
            "/api/v1/finance/donations",
            json={"parish_id": str(par_id), "amount": 1, "donation_date": "2026-05-04"},
            headers=leader_headers,
        )
        assert denied.status_code == 403, denied.text

        # MINISTRY_LEADER also cannot read donations/summary.
        denied_list = await client.get(
            f"/api/v1/finance/donations?parish_id={par_id}", headers=leader_headers
        )
        assert denied_list.status_code == 403, denied_list.text

        listing = await client.get(
            f"/api/v1/finance/donations?parish_id={par_id}", headers=auditor_headers
        )
        assert listing.status_code == 200, listing.text
        assert len(listing.json()["data"]) == 3

        # Summary aggregates per donation type with a grand total.
        summary = await client.get(
            f"/api/v1/finance/summary?parish_id={par_id}", headers=auditor_headers
        )
        assert summary.status_code == 200, summary.text
        totals = summary.json()["data"]
        assert totals["total_tithes"] == 10000
        assert totals["total_offertory"] == 5000
        assert totals["total_construction"] == 25000
        assert totals["grand_total"] == 40000
        assert totals["currency"] == "RWF"
    finally:
        if donation_ids:
            async with AsyncSessionLocal() as db:
                for did in donation_ids:
                    await db.execute(delete(Donation).where(Donation.id == uuid.UUID(did)))
                await db.commit()


# ---------------------------------------------------------------------------
# 3. Liturgy API — mass schedules and intentions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_liturgy_mass_schedules_and_intentions(client: AsyncClient, auth_users, geo_setup):
    _, _, par_id = geo_setup
    priest_headers = await auth_users(client, UserRole.PARISH_PRIEST)
    secretary_headers = await auth_users(client, UserRole.PARISH_SECRETARY)
    auditor_headers = await auth_users(client, UserRole.READ_ONLY_AUDITOR)

    mass_date = "2026-06-14"
    schedule_id = None
    intention_id = None
    try:
        # Only PARISH_PRIEST / PARISH_VICAR may schedule masses.
        sched = await client.post(
            "/api/v1/liturgy/mass-schedules",
            json={
                "parish_id": str(par_id),
                "mass_date": mass_date,
                "start_time": "10:30:00",
                "language": "rw",
                "celebrant_name": "Abbé Pierre",
            },
            headers=priest_headers,
        )
        assert sched.status_code == 201, sched.text
        schedule_id = sched.json()["data"]["id"]

        sec_sched = await client.post(
            "/api/v1/liturgy/mass-schedules",
            json={"parish_id": str(par_id), "mass_date": mass_date, "start_time": "18:00:00"},
            headers=secretary_headers,
        )
        assert sec_sched.status_code == 403, sec_sched.text

        # Auditor lists the schedule for that date.
        listing = await client.get(
            f"/api/v1/liturgy/mass-schedules?parish_id={par_id}&for_date={mass_date}",
            headers=auditor_headers,
        )
        assert listing.status_code == 200, listing.text
        assert any(row["id"] == schedule_id for row in listing.json()["data"])

        # Secretary registers an intention (stipend is part of the payload).
        intention = await client.post(
            "/api/v1/liturgy/intentions",
            json={
                "parish_id": str(par_id),
                "mass_schedule_id": schedule_id,
                "requested_by_name": "Marie Uwase",
                "intention_type": "THANKSGIVING",
                "intention_text": "Thanksgiving for a safe delivery",
                "stipend_amount": 2000,
                "scheduled_date": mass_date,
            },
            headers=secretary_headers,
        )
        assert intention.status_code == 201, intention.text
        intention_id = intention.json()["data"]["id"]
        assert intention.json()["data"]["is_paid"] is True

        # A ministry leader may not register intentions (403). (A vicar
        # inherits PARISH_SECRETARY in the RBAC hierarchy, so vicars can.)
        leader_headers = await auth_users(client, UserRole.MINISTRY_LEADER)
        leader_intention = await client.post(
            "/api/v1/liturgy/intentions",
            json={
                "parish_id": str(par_id),
                "requested_by_name": "X",
                "intention_text": "y",
                "scheduled_date": mass_date,
            },
            headers=leader_headers,
        )
        assert leader_intention.status_code == 403, leader_intention.text

        # Intentions list filtered by date and single read.
        int_list = await client.get(
            f"/api/v1/liturgy/intentions?parish_id={par_id}&target_date={mass_date}",
            headers=auditor_headers,
        )
        assert int_list.status_code == 200, int_list.text
        assert any(row["id"] == intention_id for row in int_list.json()["data"])

        got = await client.get(f"/api/v1/liturgy/intentions/{intention_id}", headers=auditor_headers)
        assert got.status_code == 200, got.text
        assert got.json()["data"]["requested_by_name"] == "Marie Uwase"

        # Unknown intention -> 404.
        missing = await client.get(f"/api/v1/liturgy/intentions/{uuid.uuid4()}", headers=auditor_headers)
        assert missing.status_code == 404, missing.text
    finally:
        async with AsyncSessionLocal() as db:
            if intention_id:
                await db.execute(delete(MassIntention).where(MassIntention.id == uuid.UUID(intention_id)))
            if schedule_id:
                await db.execute(delete(MassSchedule).where(MassSchedule.id == uuid.UUID(schedule_id)))
            await db.commit()


# ---------------------------------------------------------------------------
# 4. Archives indicators end-to-end through the statistics API (ADR 002)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_archive_indicator_documents_by_type_via_api(client: AsyncClient, auth_users, geo_setup):
    arch_id, _dea_id, par_id = geo_setup
    auditor_headers = await auth_users(client, UserRole.READ_ONLY_AUDITOR)

    doc_type = DocumentType(
        code=f"DECREE-{uuid.uuid4().hex[:8]}",
        name_en="Decree", name_fr="Décret", name_rw="Itegeko",
    )
    doc_ids = []
    async with AsyncSessionLocal() as db:
        db.add(doc_type)
        await db.flush()
        created_docs = []
        for _ in range(2):
            created_docs.append(
                Document(
                    title=f"Decree {uuid.uuid4().hex[:6]}",
                    file_path="archive/api-decree.pdf",
                    document_type_id=doc_type.id,
                    parish_id=par_id,
                )
            )
        # One document attached straight to the archdiocese.
        created_docs.append(
            Document(
                title="Curia Decree",
                file_path="archive/curia.pdf",
                document_type_id=doc_type.id,
                archdiocese_id=arch_id,
            )
        )
        db.add_all(created_docs)
        # autoflush=False: flush before relying on generated UUID ids.
        await db.flush()
        doc_ids = [doc.id for doc in created_docs]
        await db.commit()

    try:
        result = await client.get(
            f"/api/v1/statistics/indicators/documents_by_type?archdiocese_id={arch_id}",
            headers=auditor_headers,
        )
        assert result.status_code == 200, result.text
        rows = result.json()["data"]["rows"]
        matching = [r for r in rows if r["group_id"] == str(doc_type.id)]
        assert len(matching) == 1
        assert matching[0]["group_name"] == "Decree"
        assert matching[0]["value"] == 3  # two parish docs + one curia doc
    finally:
        async with AsyncSessionLocal() as db:
            for did in doc_ids:
                await db.execute(delete(Document).where(Document.id == did))
            await db.execute(delete(DocumentType).where(DocumentType.id == doc_type.id))
            await db.commit()
