#!/usr/bin/env bash
# Arkidi Platform – one-off PostgreSQL+PostGIS backup (pg_dump, custom format).
# For scheduled backups use the `backup` service in docker-compose.prod.yml.
#
# Usage:
#   DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
#   DB_USER=arkidi_user DB_PASSWORD=secret BACKUP_DIR=./backups \
#   ./scripts/backup.sh
set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-arkidi_db}"
DB_USER="${DB_USER:-arkidi_user}"
DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD environment variable is required}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"

TS="$(date +%Y%m%d_%H%M%S)"
OUT="${BACKUP_DIR}/arkidi_${TS}.dump"
mkdir -p "${BACKUP_DIR}"

echo "[backup] Dumping ${DB_NAME}@${DB_HOST}:${DB_PORT} -> ${OUT}"

PGPASSWORD="${DB_PASSWORD}" pg_dump \
    --no-owner --no-acl \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -Fc \
    > "${OUT}"

echo "[backup] Done: ${OUT} ($(du -h "${OUT}" | cut -f1))"