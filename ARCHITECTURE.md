# Arkidi Platform Architecture Specification

## 1. Architectural Philosophy: Modular Monolith

Arkidi Platform is structured as a **Modular Monolith**. It guarantees clear separation of concerns, high cohesion within business domains, and loose coupling across domain boundaries.

```
                    ┌─────────────────────────────────────────┐
                    │       Arkidi React + Vite Frontend      │
                    │  (TypeScript, Tailwind CSS, Leaflet)   │
                    └────────────────────┬────────────────────┘
                                         │ HTTP / JSON / JWT
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │             FastAPI Gateway             │
                    │    (Auth, Rate Limit, i18n Middleware)  │
                    └────────────────────┬────────────────────┘
                                         │
 ┌───────────────────────────────────────┴───────────────────────────────────────┐
 │                                                                               │
 ▼                                       ▼                                       ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│     Auth     │ │  Geography   │ │   Faithful   │ │  Sacraments  │ │    Clergy    │
│    Module    │ │    Module    │ │    Module    │ │    Module    │ │    Module    │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
 │                                       │                                       │
 ▼                                       ▼                                       ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Liturgy    │ │   Finance    │ │  Ministries  │ │ Land Assets  │ │   Archive    │
│    Module    │ │    Module    │ │    Module    │ │ (PostGIS GIS)│ │ & Statistics │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │      Shared Core & Common Services      │
                    │  (Async Engine, Redis, Celery, PDF, QR) │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │      PostgreSQL 16 + PostGIS Database   │
                    └─────────────────────────────────────────┘
```

---

## 2. Bounded Contexts & Module Responsibilities

### `auth`
- User management, passwords (Argon2), JWT token generation and refresh.
- Role-Based Access Control (RBAC):
  * `SUPER_ADMIN` (Archdiocesan IT/Archbishopric Admin)
  * `CHANCELLOR` (Archdiocesan Chancellor - Official decrees & registers)
  * `ECONOMO` (Archdiocesan Treasurer / Land & Asset Director)
  * `DEAN` (Curé de Doyenné / Vicar Forane)
  * `PARISH_PRIEST` (Curé de Paroisse)
  * `PARISH_VICAR` (Vicaire paroissial)
  * `PARISH_SECRETARY` (Secrétaire paroissial - Data entry & certificates)
  * `MINISTRY_LEADER` (Responsable de commission / mouvement)
  * `READ_ONLY_AUDITOR` (Auditeur / Statistician)

### `geography`
- Canonical and civil spatial hierarchy:
  * Archdiocese of Kigali (Archidiocèse de Kigali)
  * Deaneries (Doyennés: e.g., Sainte Famille, Saint Michel, Kicukiro, Nyamata, etc.)
  * Parishes (Paroisses)
  * Sub-Parishes / Centrales (Succursales)
  * Small Christian Communities (CEB / Imiryango-remezo)

### `faithful`
- Parishioner canonical profiles:
  * Full name, Christian name, gender, date and place of birth.
  * National ID (NID), phone, email, residence address.
  * Household / Family head and relationship linking.
  * Canonical status (Catechumen, Baptized, In Regular Marriage, etc.).

### `sacraments`
- Official Roman Catholic Sacramental Registers (Canonical Book, Volume, Page, Act Number):
  * **Baptism (Baptême)**: Date, celebrant, godparents, parents, annotations (subsequent confirmation/marriage/orders).
  * **First Communion (Première Communion)**: Date, parish, celebrant.
  * **Confirmation (Confirmation)**: Date, administering bishop/vicar, sponsor (marraine/parrain).
  * **Matrimony (Mariage canonique)**: Bride, groom, banns publication, witnesses, priest celebrant, canonical dispensations/impediments.
  * **Holy Orders (Ordre sacré)**: Diaconate, Priesthood, Episcopate, ordaining prelate.
  * **Religious Profession (Profession religieuse)**: Temporary & perpetual vows, congregation/institute.
  * **Anointing of the Sick & Funerals (Onction & Sépulture)**: Date of death, burial site, celebrant.

### `clergy`
- Priests, Deacons, Seminarians, and Religious personnel registry.
- Canonical faculties, current assignment (Curé, Vicaire, Aumônier), biography, and ordination timeline.

### `liturgy`
- Mass schedule (Centrales, languages: Kinyarwanda, French, English).
- Mass intentions ledger: Intentions for the dead (*Requiem*), Thanksgiving (*Action de grâce*), Special petitions.
- Stipend tracking & celebrant assignment.

### `finance`
- Parish and Archdiocesan financial ledger:
  * Church offerings (*Amaturo* / *Dîmes*)
  * Building campaign contributions / Pledges
  * Mass stipend allocation to priests
  * Receipt generation and audit trails.

### `ministries`
- Pastoral Commissions (Catechesis, Liturgy, Caritas, Justice & Peace, Youth, Family).
- Catholic Action Movements & Lay Associations (Legion of Mary, Charismatic Renewal, Choirs, Scout/Guides).

### `land_assets`
- Land parcels with GeoAlchemy2 PostGIS polygons (`SRID 4326`).
- Cadastral UPI numbers, title deeds, land boundaries, boundary disputes tracking, lease agreements, buildings on diocesan land.

### `archive`
- Digital archive of physical historical registry books.
- Scanned register pages, OCR indexing, secure digital vault, and certificate verification QR code subsystem.

### `statistics`
- Holy See annual reporting (*Annuario Pontificio* extracts).
- Annual Parish statistical returns (baptisms, conversions, marriages, active faithful count, school pupils, deaths).
- Spatial choropleth and demographic analytics.

---

## 3. Module Internal Structure Convention

Every backend domain module strictly implements the 6-file clean architecture pattern:
```
module_name/
├── __init__.py       # Exports router, models, schemas
├── models.py         # SQLAlchemy 2.0 ORM models (DeclarativeBase)
├── schemas.py        # Pydantic v2 schemas (Base, Create, Update, Response)
├── repository.py     # Data access layer (async SQLAlchemy sessions)
├── service.py        # Business logic, validations, domain rules
├── router.py         # FastAPI APIRouter endpoints
└── exceptions.py     # Domain-specific HTTP/business exceptions
```

---

## 4. Internationalization (i18n)

- Languages supported:
  * **English (`en`)**: International communication & diocesan reporting.
  * **French (`fr`)**: Canonical documents, official correspondence & certificates.
  * **Kinyarwanda (`rw`)**: Pastoral parish records, liturgical announcements & parishioner communications.
- Frontend: `i18next` with JSON dictionaries.
- Backend: `Accept-Language` header parsing and localized error/status responses.
