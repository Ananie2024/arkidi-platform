#!/usr/bin/env bash
# Arkidi Platform – restore a PostgreSQL+PostGIS dump into a target database.
#
# Usage:
#   DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
#   DB_USER=arkidi_user DB_PASSWORD=secret \
#   ./scripts/restore.sh /path/to/arkidi_TIMESTAMP.dump
#
# Recommend restoring into a freshly created empty database to avoid object
# conflicts; `--clean --if-exists` drops existing objects first.
set -euo pipefail

DUMP="${1:?Usage: restore.sh <dumpfile>}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-arkidi_db}"
DB_USER="${DB_USER:-arkidi_user}"
DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD environment variable is required}"

[ -f "${DUMP}" ] || { echo "Dump file not found: ${DUMP}" >&2; exit 1; }

echo "[restore] Restoring ${DUMP} into ${DB_NAME}@${DB_HOST}:${DB_PORT} as ${DB_USER} ..."

PGPASSWORD="${DB_PASSWORD}" pg_restore \
    --no-owner --no-acl --clean --if-exists \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" "${DUMP}"

echo "[restore] Complete."