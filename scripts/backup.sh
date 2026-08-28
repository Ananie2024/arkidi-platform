#!/usr/bin/env bash
# Arkidi Platform – one-off PostgreSQL+PostGIS backup + archive of uploaded
# file-storage (documents, photos, scanned registers).
# For scheduled backups use the `backup` service in docker-compose.prod.yml.
#
# Usage:
#   DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
#   DB_USER=arkidi_user DB_PASSWORD=secret BACKUP_DIR=./backups \
#   FILE_STORAGE_PATH=./file-storage \
#   ./scripts/backup.sh
set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-arkidi_db}"
DB_USER="${DB_USER:-arkidi_user}"
DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD environment variable is required}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
FILE_STORAGE_PATH="${FILE_STORAGE_PATH:-./file-storage}"

TS="$(date +%Y%m%d_%H%M%S)"
OUT="${BACKUP_DIR}/arkidi_${TS}.dump"
FILES_TARBALL="${BACKUP_DIR}/arkidi_file_storage_${TS}.tar.gz"
mkdir -p "${BACKUP_DIR}"

echo "[backup] Dumping ${DB_NAME}@${DB_HOST}:${DB_PORT} -> ${OUT}"

PGPASSWORD="${DB_PASSWORD}" pg_dump \
    --no-owner --no-acl \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -Fc \
    > "${OUT}"

if [ -d "${FILE_STORAGE_PATH}" ] && [ -n "$(ls -A "${FILE_STORAGE_PATH}" 2>/dev/null)" ]; then
    echo "[backup] Archiving file-storage ${FILE_STORAGE_PATH} -> ${FILES_TARBALL}"
    (cd "$(dirname "${FILE_STORAGE_PATH}")" && tar -czf "${FILES_TARBALL}" "$(basename "${FILE_STORAGE_PATH}")")
else
    echo "[backup] file-storage '${FILE_STORAGE_PATH}' is empty/missing; skipping tarball."
fi

echo "[backup] Done: ${OUT} ($(du -h "${OUT}" | cut -f1))"
if [ -f "${FILES_TARBALL}" ]; then
    echo "[backup] Done: ${FILES_TARBALL} ($(du -h "${FILES_TARBALL}" | cut -f1))"
fi