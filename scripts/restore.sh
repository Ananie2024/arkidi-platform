#!/usr/bin/env bash
# Arkidi Platform – restore a PostgreSQL+PostGIS dump into a target database
# and, optionally, restore the archived file-storage tarball produced by
# backup.sh.
#
# Usage:
#   DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
#   DB_USER=arkidi_user DB_PASSWORD=secret \
#   ./scripts/restore.sh /path/to/arkidi_TIMESTAMP.dump [/path/to/arkidi_file_storage_TIMESTAMP.tar.gz]
#
# The optional second argument (a file-storage tarball produced by backup.sh) is
# extracted into FILE_STORAGE_PATH (default ./file-storage).
#
# Recommend restoring into a freshly created empty database to avoid object
# conflicts; `--clean --if-exists` drops existing objects first.
set -euo pipefail

DUMP="${1:?Usage: restore.sh <dumpfile> [file_storage.tgz]}"
FILE_STORAGE_TARBALL="${2:-}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-arkidi_db}"
DB_USER="${DB_USER:-arkidi_user}"
DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD environment variable is required}"
FILE_STORAGE_PATH="${FILE_STORAGE_PATH:-./file-storage}"

[ -f "${DUMP}" ] || { echo "Dump file not found: ${DUMP}" >&2; exit 1; }

echo "[restore] Restoring ${DUMP} into ${DB_NAME}@${DB_HOST}:${DB_PORT} as ${DB_USER} ..."

PGPASSWORD="${DB_PASSWORD}" pg_restore \
    --no-owner --no-acl --clean --if-exists \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" "${DUMP}"

if [ -n "${FILE_STORAGE_TARBALL}" ]; then
    [ -f "${FILE_STORAGE_TARBALL}" ] || { echo "File-storage tarball not found: ${FILE_STORAGE_TARBALL}" >&2; exit 1; }
    mkdir -p "${FILE_STORAGE_PATH}"
    echo "[restore] Extracting file-storage ${FILE_STORAGE_TARBALL} -> ${FILE_STORAGE_PATH}"
    tar -xzf "${FILE_STORAGE_TARBALL}" -C "$(dirname "${FILE_STORAGE_PATH}")"
    echo "[restore] File-storage restored."
fi

echo "[restore] Complete."