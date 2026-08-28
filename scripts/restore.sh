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
#
# The target database must already have the PostGIS extension provisioned (e.g.
# by the DBA/admin role, or via `scripts/restore_drill.sh`). This restore restores
# the *application* schema and data only and deliberately skips the
# PostGIS-infrastructure entries that pg_dump records (CREATE/COMMENT ON the
# `postgis` extension and the `spatial_ref_sys` table). Those are owned/managed
# by the PostGIS extension itself and, unlike the app tables, cannot be created
# or written by a non-superuser application role:
#
#   pg_restore: error: could not execute query: ERROR:  permission denied to
#   create extension "postgis"
#
# By provisioning PostGIS separately (as a superuser) and excluding those TOC
# entries here, a restore runs cleanly under a non-superuser application role.
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

# Build a filtered pg_restore list that excludes the PostGIS-infrastructure TOC
# entries described above. pg_restore --list emits the exact "restore list"
# format that --use-list accepts, so we can safely remove the lines we must not
# touch and hand the result back to pg_restore.
RESTORE_LIST="$(mktemp)"
FILTERED_LIST="$(mktemp)"
trap 'rm -f "${RESTORE_LIST}" "${FILTERED_LIST}"' EXIT

PGPASSWORD="${DB_PASSWORD}" pg_restore --list "${DUMP}" > "${RESTORE_LIST}"
grep -Evi 'postgis|spatial_ref_sys' "${RESTORE_LIST}" > "${FILTERED_LIST}" || true

PGPASSWORD="${DB_PASSWORD}" pg_restore \
    --no-owner --no-acl --clean --if-exists \
    --use-list "${FILTERED_LIST}" \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" "${DUMP}"

rm -f "${RESTORE_LIST}" "${FILTERED_LIST}"
trap - EXIT

if [ -n "${FILE_STORAGE_TARBALL}" ]; then
    [ -f "${FILE_STORAGE_TARBALL}" ] || { echo "File-storage tarball not found: ${FILE_STORAGE_TARBALL}" >&2; exit 1; }
    mkdir -p "${FILE_STORAGE_PATH}"
    echo "[restore] Extracting file-storage ${FILE_STORAGE_TARBALL} -> ${FILE_STORAGE_PATH}"
    tar -xzf "${FILE_STORAGE_TARBALL}" -C "$(dirname "${FILE_STORAGE_PATH}")"
    echo "[restore] File-storage restored."
fi

echo "[restore] Complete."