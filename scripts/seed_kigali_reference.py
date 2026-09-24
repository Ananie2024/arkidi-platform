"""
Archdiocese of Kigali Reference Seeding Script
Provisions canonical geography (Archdiocese -> Deaneries -> Parishes),
catalog of document types, and land-use categories for production/staging.

Idempotent: safe to run multiple times without duplicating entities.
"""

import asyncio
from datetime import date
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.deanery import Archdiocese, Deanery
from app.models.parish import Parish, Centrale, SmallChristianCommunity
from app.models.document_type import DocumentType
from app.models.land_use_category import LandUseCategory


KIGALI_DEANERIES = [
    {
        "name": "Doyenné Sainte-Famille",
        "code": "DOY-SF",
        "vicar": "Abbé Jean-Baptiste Gahamanyi",
        "parishes": [
            {
                "name": "Paroisse Sainte-Famille",
                "code": "PAR-SF",
                "patron_saint": "Sainte Famille de Nazareth",
                "establishment_date": date(1913, 11, 20),
                "district": "Nyarugenge",
                "sector": "Nyarugenge",
                "address": "KN 2 Ave, Ville de Kigali",
                "centrales": ["Centrale Sainte Famille", "Centrale Rugenge"],
            },
            {
                "name": "Paroisse Saint-Pierre Nyamirambo",
                "code": "PAR-SPN",
                "patron_saint": "Saint Pierre Apôtre",
                "establishment_date": date(1962, 7, 1),
                "district": "Nyarugenge",
                "sector": "Nyamirambo",
                "address": "KN 3 Ave, Nyamirambo",
                "centrales": ["Centrale Nyamirambo", "Centrale Mumena"],
            },
            {
                "name": "Paroisse Charles Lwanga Nyamirambo",
                "code": "PAR-CLN",
                "patron_saint": "Saint Charles Lwanga",
                "establishment_date": date(1982, 6, 3),
                "district": "Nyarugenge",
                "sector": "Rwezamenyo",
                "address": "Rwezamenyo, Kigali",
                "centrales": ["Centrale Rwezamenyo"],
            },
        ],
    },
    {
        "name": "Doyenné Saint-Michel",
        "code": "DOY-SM",
        "vicar": "Abbé Innocent Consolateur",
        "parishes": [
            {
                "name": "Cathédrale Saint-Michel",
                "code": "PAR-CSM",
                "patron_saint": "Saint Michel Archange",
                "establishment_date": date(1963, 9, 29),
                "district": "Nyarugenge",
                "sector": "Kiyovu",
                "address": "KN 4 Ave, Kiyovu",
                "centrales": ["Centrale Cathédrale", "Centrale Kiyovu"],
            },
            {
                "name": "Paroisse Regina Pacis Remera",
                "code": "PAR-RPR",
                "patron_saint": "Regina Pacis (Reine de la Paix)",
                "establishment_date": date(1993, 8, 15),
                "district": "Gasabo",
                "sector": "Remera",
                "address": "KG 11 Ave, Remera",
                "centrales": ["Centrale Remera", "Centrale Nyarutarama"],
            },
            {
                "name": "Paroisse Saint-Ignace Kibagabaga",
                "code": "PAR-SIK",
                "patron_saint": "Saint Ignace de Loyola",
                "establishment_date": date(2007, 7, 31),
                "district": "Gasabo",
                "sector": "Kimironko",
                "address": "KG 19 Ave, Kibagabaga",
                "centrales": ["Centrale Kibagabaga"],
            },
            {
                "name": "Paroisse Sainte-Anne Kimihurura",
                "code": "PAR-SAK",
                "patron_saint": "Sainte Anne",
                "establishment_date": date(2018, 7, 26),
                "district": "Gasabo",
                "sector": "Kimihurura",
                "address": "KG 28 Ave, Kimihurura",
                "centrales": ["Centrale Kimihurura"],
            },
        ],
    },
    {
        "name": "Doyenné Kicukiro",
        "code": "DOY-KCK",
        "vicar": "Abbé Eugène Twahirwa",
        "parishes": [
            {
                "name": "Paroisse Saint-Jean-Bosco Kicukiro",
                "code": "PAR-SJB",
                "patron_saint": "Saint Jean Bosco",
                "establishment_date": date(1966, 1, 31),
                "district": "Kicukiro",
                "sector": "Kicukiro",
                "address": "KK 15 Rd, Centre Kicukiro",
                "centrales": ["Centrale Kicukiro", "Centrale Niboye"],
            },
            {
                "name": "Paroisse Sainte-Marie Gikondo",
                "code": "PAR-SMG",
                "patron_saint": "Sainte Marie Mère de Dieu",
                "establishment_date": date(1968, 8, 15),
                "district": "Kicukiro",
                "sector": "Gikondo",
                "address": "KK 31 Ave, Gikondo",
                "centrales": ["Centrale Gikondo", "Centrale Kanserege"],
            },
            {
                "name": "Paroisse Saint-Joseph Masaka",
                "code": "PAR-SJM",
                "patron_saint": "Saint Joseph Artisan",
                "establishment_date": date(1998, 5, 1),
                "district": "Kicukiro",
                "sector": "Masaka",
                "address": "RN 3, Masaka",
                "centrales": ["Centrale Masaka", "Centrale Rusheshe"],
            },
            {
                "name": "Paroisse Saint-Paul Gahanga",
                "code": "PAR-SPG",
                "patron_saint": "Saint Paul Apôtre",
                "establishment_date": date(2012, 6, 29),
                "district": "Kicukiro",
                "sector": "Gahanga",
                "address": "KK 54 Ave, Gahanga",
                "centrales": ["Centrale Gahanga", "Centrale Karembure"],
            },
        ],
    },
    {
        "name": "Doyenné Nyamata",
        "code": "DOY-NYM",
        "vicar": "Abbé Emmanuel Nsengiyumva",
        "parishes": [
            {
                "name": "Paroisse Nyamata",
                "code": "PAR-NYM",
                "patron_saint": "Notre-Dame de la Miséricorde",
                "establishment_date": date(1957, 10, 7),
                "district": "Bugesera",
                "sector": "Nyamata",
                "address": "Centre Nyamata, Bugesera",
                "centrales": ["Centrale Nyamata", "Centrale Kanzenze"],
            },
            {
                "name": "Paroisse Ruhuha",
                "code": "PAR-RUH",
                "patron_saint": "Sainte Thérèse de l'Enfant Jésus",
                "establishment_date": date(1969, 10, 1),
                "district": "Bugesera",
                "sector": "Ruhuha",
                "address": "Ruhuha, Bugesera",
                "centrales": ["Centrale Ruhuha", "Centrale Bihari"],
            },
            {
                "name": "Paroisse Mayange",
                "code": "PAR-MAY",
                "patron_saint": "Saint Jean-Baptiste",
                "establishment_date": date(1984, 6, 24),
                "district": "Bugesera",
                "sector": "Mayange",
                "address": "Mayange, Bugesera",
                "centrales": ["Centrale Mayange", "Centrale Muyenzi"],
            },
            {
                "name": "Paroisse Rilima",
                "code": "PAR-RIL",
                "patron_saint": "Saints Archanges",
                "establishment_date": date(1960, 9, 29),
                "district": "Bugesera",
                "sector": "Rilima",
                "address": "Rilima, Bugesera",
                "centrales": ["Centrale Rilima", "Centrale Karera"],
            },
        ],
    },
]

LAND_USE_CATEGORIES = [
    {
        "code": "CHURCH_COMPOUND",
        "name_en": "Church & Parish Compound",
        "name_fr": "Enceinte paroissiale et église",
        "name_rw": "Urubuga rw'ingoro n'ubupadiri",
        "description": "Church building, presbytery (rectory), parish hall, and pastoral office grounds.",
    },
    {
        "code": "SCHOOL_EDUCATION",
        "name_en": "Diocesan Schools & Education",
        "name_fr": "Écoles diocésaines et enseignement",
        "name_rw": "Amashuri ya Diyosezi",
        "description": "Primary and secondary schools, vocational training centres, and seminaries.",
    },
    {
        "code": "HEALTH_HOSPITAL",
        "name_en": "Health Centres & Dispensaries",
        "name_fr": "Centres de santé et dispensaires",
        "name_rw": "Ibigo nderabuzima",
        "description": "Parish dispensaries, maternity clinics, and Caritas health facilities.",
    },
    {
        "code": "AGRICULTURAL",
        "name_en": "Farmland & Agroforestry",
        "name_fr": "Terres agricoles et agroforesterie",
        "name_rw": "Ubutaka bw'ubuhinzi n'amashyamba",
        "description": "Parish tea/coffee plantations, farming land, and forestry reserves.",
    },
    {
        "code": "COMMERCIAL_LEASE",
        "name_en": "Commercial & Rental Real Estate",
        "name_fr": "Immobilier commercial et locatif",
        "name_rw": "Inyubako z'ubucuruzi n'ubukode",
        "description": "Income-generating rental apartments, commercial centres, and leased halls.",
    },
]

DOCUMENT_TYPES = [
    {
        "code": "SACRAMENTAL_REGISTER",
        "name_en": "Sacramental Register Volume",
        "name_fr": "Registre sacramentel paroissial",
        "name_rw": "Igitabo cy'amasakaramentu",
        "category": "SACRAMENTS",
        "retention_years": None,
        "disposition_action": "PRESERVE_INDEFINITELY",
        "description": "Historic paper and digital sacramental books (Baptism, Confirmation, Marriage).",
    },
    {
        "code": "CANONICAL_DECREE",
        "name_en": "Canonical Decree & Dispensation",
        "name_fr": "Décret canonique et dispense",
        "name_rw": "Icyemezo cya Kiliziya n'imbabazi",
        "category": "CANONICAL",
        "retention_years": None,
        "disposition_action": "PRESERVE_INDEFINITELY",
        "description": "Archdiocesan decrees, matrimonial dispensations, canonical declarations.",
    },
    {
        "code": "TITLE_DEED",
        "name_en": "Cadastral Title Deed & Land Survey",
        "name_fr": "Titre de propriété foncière et cadastre",
        "name_rw": "Icyangombwa cy'ubutaka",
        "category": "LAND",
        "retention_years": None,
        "disposition_action": "PRESERVE_INDEFINITELY",
        "description": "Official Rwanda Land Management Authority (RLMA) UPI certificates and deed contracts.",
    },
    {
        "code": "FINANCIAL_AUDIT",
        "name_en": "Annual Financial Audit & Ledger",
        "name_fr": "Rapport d'audit financier annuel",
        "name_rw": "Raporo y'ibaruramari",
        "category": "FINANCE",
        "retention_years": 10,
        "disposition_action": "TRANSFER",
        "description": "Annual parish balance sheets, archdiocesan audit returns, and bank statements.",
    },
    {
        "code": "PASTORAL_LETTER",
        "name_en": "Archbishop Pastoral Letter & Circular",
        "name_fr": "Lettre pastorale de l'Archevêque",
        "name_rw": "Ibaruwa y'ubushumba",
        "category": "PASTORAL",
        "retention_years": None,
        "disposition_action": "PRESERVE_INDEFINITELY",
        "description": "Archbishop homilies, pastoral council directives, and liturgical instructions.",
    },
]


async def seed_kigali_reference():
    async with AsyncSessionLocal() as session:
        print("✝ Seeding Archdiocese of Kigali canonical hierarchy & reference catalogs...")

        # 1. Archdiocese
        arch_res = await session.execute(
            select(Archdiocese).where(Archdiocese.name == "Archidiocèse de Kigali")
        )
        archdiocese = arch_res.scalar_one_or_none()
        if not archdiocese:
            archdiocese = Archdiocese(
                name="Archidiocèse de Kigali",
                canonical_erection_date=date(1976, 4, 10),
                patron_saint="Saint Michel Archange",
                see_city="Kigali",
            )
            session.add(archdiocese)
            await session.flush()
            print("✓ Provisioned Archidiocèse de Kigali")
        else:
            print("✓ Archidiocèse de Kigali already exists")

        # 2. Deaneries & Parishes
        for d_info in KIGALI_DEANERIES:
            d_res = await session.execute(select(Deanery).where(Deanery.code == d_info["code"]))
            deanery = d_res.scalar_one_or_none()
            if not deanery:
                deanery = Deanery(
                    archdiocese_id=archdiocese.id,
                    name=d_info["name"],
                    code=d_info["code"],
                    vicar_forane_name=d_info["vicar"],
                )
                session.add(deanery)
                await session.flush()
                print(f"  ✓ Created {d_info['name']} ({d_info['code']})")

            for p_info in d_info["parishes"]:
                p_res = await session.execute(select(Parish).where(Parish.code == p_info["code"]))
                parish = p_res.scalar_one_or_none()
                if not parish:
                    parish = Parish(
                        deanery_id=deanery.id,
                        name=p_info["name"],
                        code=p_info["code"],
                        patron_saint=p_info["patron_saint"],
                        establishment_date=p_info["establishment_date"],
                        district=p_info["district"],
                        sector=p_info["sector"],
                        address=p_info["address"],
                    )
                    session.add(parish)
                    await session.flush()
                    print(
                        f"    ✓ Created Parish: {p_info['name']} [{p_info['district']}/{p_info['sector']}]"
                    )

                    # Add default Centrales
                    for c_name in p_info.get("centrales", []):
                        centrale = Centrale(
                            parish_id=parish.id,
                            name=c_name,
                            code=f"{p_info['code']}-{c_name[:3].upper()}",
                        )
                        session.add(centrale)
                        await session.flush()

                        # Add a default CEB
                        ceb = SmallChristianCommunity(
                            centrale_id=centrale.id,
                            name=f"CEB Saint-Paul ({c_name})",
                        )
                        session.add(ceb)

        # 3. Land Use Categories
        for cat in LAND_USE_CATEGORIES:
            c_res = await session.execute(
                select(LandUseCategory).where(LandUseCategory.code == cat["code"])
            )
            if not c_res.scalar_one_or_none():
                session.add(LandUseCategory(**cat))
                print(f"  ✓ Provisioned LandUseCategory: {cat['code']}")

        # 4. Document Types
        for doc in DOCUMENT_TYPES:
            doc_res = await session.execute(
                select(DocumentType).where(DocumentType.code == doc["code"])
            )
            if not doc_res.scalar_one_or_none():
                session.add(DocumentType(**doc))
                print(f"  ✓ Provisioned DocumentType: {doc['code']}")

        await session.commit()
        print("\n✨ Archdiocese of Kigali canonical reference seed completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_kigali_reference())
