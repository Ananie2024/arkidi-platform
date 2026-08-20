# Arkidi Platform
**Archdiocese of Kigali Digital Archive, Parish Management & Statistical System**

Arkidi Platform is a unified, enterprise-grade modular monolith software system built for the Catholic Archdiocese of Kigali (Archidiocèse de Kigali). It integrates digital parish administration, canonical sacramental registries, archdiocesan land intelligence (GIS), financial management, and pontifical statistical reporting.

---

## 🏛️ System Overview & Capabilities

- **Ecclesiastical & Civil Geography**: Multi-tier hierarchy: Archdiocese → Deaneries (Doyennés) → Parishes (Paroisses) → Centrales (Succursales) → Small Christian Communities (CEB / Imiryango-remezo).
- **Faithful & Household Registry**: Comprehensive parishioner profiles, family units, canonical status, and demographic records.
- **Canonical Sacraments & Registers**: Full Catholic canonical registry workflows for Baptism, First Communion, Confirmation, Matrimony, Holy Orders, Religious Profession, Anointing, and Christian Funerals. Includes official certificate generation with verification QR codes.
- **Land Intelligence & Real Estate GIS**: PostGIS-powered geospatial tracking of parish land parcels, cadastral UPI numbers, deed archives, boundary polygons, and asset management.
- **Liturgical Management & Mass Intentions**: Mass scheduling across centrales, mass intentions ledger, and stipend accounting.
- **Parish & Archdiocesan Finance**: Tithes (*amaturo / amaturo y'umuryango*), campaign donations, financial ledgers, and auditable receipting.
- **Clergy & Religious Roster**: Profiles, canonical faculties, assignments, and historical appointments of priests, deacons, and religious men & women.
- **Pastoral Ministries & Lay Apostolate**: Management of pastoral councils, commissions, choirs, and Catholic Action movements (*Legion of Mary, Caritas, Youth*, etc.).
- **Digital Archive & Document Storage**: Archival scan ingestion for historic sacramental registries, OCR metadata indexing, and shelf/volume cataloging.
- **Pontifical Statistics & Reporting**: Automated generation of the annual diocesan statistical report for the Holy See (*Annuario Pontificio*), demographic trends, and parish KPIs.
- **Multi-Language Support (i18n)**: Native English, French (*Français*), and Kinyarwanda (*Ikinyarwanda*).

---

## 🛠️ Technology Stack

| Tier | Technologies |
|---|---|
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), GeoAlchemy2, Alembic |
| **Database & GIS** | PostgreSQL 16 + PostGIS 3.4, Redis 7 (Caching, Token Blacklist, Celery Broker) |
| **Async Tasks** | Celery 5.3 + Redis |
| **Security & Auth** | JWT (PyJWT) + Argon2-cffi, Role-Based Access Control (RBAC) |
| **GIS & Docs** | Shapely, Pyproj, ReportLab (PDF Certificates), Qrcode (PIL) |
| **Frontend** | React 19 / Vite, TypeScript, Tailwind CSS, TanStack Query, React Hook Form + Zod, Zustand, React Leaflet (GIS Maps), i18next |
| **DevOps** | Docker, Docker Compose, Nginx |

---

## 🚀 Quick Start (Development)

### 1. Prerequisites
- Docker and Docker Compose
- *Or* Local Python 3.11+, Node.js 20+, PostgreSQL with PostGIS, and Redis

### 2. Environment Setup
```bash
# Clone and navigate to project root
cd arkidi-platform

# Copy environment configurations
cp .env.example .env        # Backend: local development
cp frontend/.env.example frontend/.env  # Frontend: local development
```

### 3. Run with Docker Compose
```bash
docker-compose up --build -d
```
- **Frontend App**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Interactive OpenAPI Docs (Swagger)**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

---

## 🚀 Quick Start (Production)

### 1. Environment Setup
```bash
# Clone and navigate to project root
cd arkidi-platform

# Copy production environment configurations
cp .env.production.example .env.production  # Backend: production (fill in real secrets)
cp frontend/.env.production.example frontend/.env.production  # Frontend: production (update API URL)
```

Edit `.env.production` and replace all `<<PLACEHOLDER>>` values with real production secrets.

### 2. Deploy with Docker Compose (Production)
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

---

## 📁 Repository Architecture

Arkidi Platform is structured as a clean **Modular Monolith**:
- `backend/app/modules/`: High-cohesion domain modules (`auth`, `geography`, `faithful`, `sacraments`, `clergy`, `liturgy`, `finance`, `ministries`, `land_assets`, `archive`, `statistics`).
- `backend/app/core/`: Core infrastructure (database, security, redis, celery, middleware, permissions).
- `backend/app/common/`: Shared utilities (i18n, pagination, PDF generator, QR generator, storage).
- `frontend/src/modules/`: Frontend feature modules matching backend domain boundaries.
- `frontend/src/i18n/`: Tri-lingual translation keys (EN, FR, RW).

See `ARCHITECTURE.md` for full architectural documentation.
