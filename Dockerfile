FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies (including GIS libraries: GDAL, GEOS, PROJ)
# postgresql-client provides pg_dump / pg_restore / psql needed by the
# Celery backup & restore-drill tasks (see app/tasks/backups.py).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    # Tesseract OCR engine + language packs for the archive OCR worker
    # (app/tasks/archive_ocr.py). `eng` ships inside the tesseract-ocr
    # package; `fra` covers the French-language historical ledgers.
    tesseract-ocr \
    tesseract-ocr-fra \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create dedicated non-root application user and group
RUN groupadd -r -g 1001 arkidi && useradd -r -u 1001 -g arkidi -d /app -s /sbin/nologin arkidi

# Create storage and logs directories, ensuring correct ownership
RUN mkdir -p /app/file-storage /app/logs /app/backups && \
    chown -R arkidi:arkidi /app

EXPOSE 8000

# Entrypoint: waits for Postgres (bounded retries), applies `alembic upgrade
# head`, then execs the real uvicorn command. See docker-entrypoint.sh.
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

USER arkidi

ENTRYPOINT ["/docker-entrypoint.sh"]
