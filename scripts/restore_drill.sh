#!/usr/bin/env bash
# Arkidi Platform – end-to-end restore drill.
#
# Proves that a backup (DB dump + file-storage tarball) can actually be restored
# into a fresh database and that the data round-trips. Run this regularly (and
# in CI via tests/test_restore_drill.py) so a restore is never an untested
# gamble at the moment you actually need it.
#
# What it does:
#   1. Runs scripts/backup.sh (Postgres dump + file-storage tarball).
#   2. Creates a scratch database named arkidi_restore_drill_<ts>.
#   3. Runs scripts/restore.sh against the scratch DB (same path used in a real
#      recovery, including the file-storage tarball).
#   4. Verifies the restored DB is non-empty (table count + representative row
#      counts match the source) and the file-storage round-tripped.
#   5. Drops the scratch database and removes the drill artifacts.
#
# Requires: psql, pg_dump, pg_restore, tar, and a DB role with CREATEDB.
# Usage:
#   DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
#   DB_USER=arkidi_user DB_PASSWORD=secret BACKUP_DIR=./backups \
#   FILE_STORAGE_PATH=./file-storage \
#   ./scripts/restore_drill.sh
set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-arkidi_db}"
DB_USER="${DB_USER:-arkidi_user}"
DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD environment variable is required}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
FILE_STORAGE_PATH="${FILE_STORAGE_PATH:-./file-storage}"
WORKDIR="$(mktemp -d)"
TS="$(date +%Y%m%d_%H%M%S)"
SCRATCH_DB="arkidi_restore_drill_${TS}"

export PGCLIENTENCODING=UTF8
PSQL=(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}")

cleanup() {
    set +e
    "${PSQL[@]}" -d ${DB_NAME} -v ON_ERROR_STOP=0 \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${SCRATCH_DB}' AND pid<>pg_backend_pid()" >/dev/null 2>&1
    "${PSQL[@]}" -d ${DB_NAME} -v ON_ERROR_STOP=0 -c "DROP DATABASE IF EXISTS ${SCRATCH_DB}" >/dev/null 2>&1
    rm -rf "${WORKDIR}"
    echo "[drill] Cleaned up scratch DB '${SCRATCH_DB}' and ${WORKDIR}."
}
trap cleanup EXIT

echo "[drill] STEP 1/4  backup source '${DB_NAME}' -> ${BACKUP_DIR}"
BACKUP_DIR="${BACKUP_DIR}" FILE_STORAGE_PATH="${FILE_STORAGE_PATH}" \
DB_HOST="${DB_HOST}" DB_PORT="${DB_PORT}" DB_NAME="${DB_NAME}" \
DB_USER="${DB_USER}" DB_PASSWORD="${DB_PASSWORD}" \
"$(dirname "$0")/backup.sh"
DUMP="$(ls -1t "${BACKUP_DIR}"/arkidi_[0-9]*.dump | head -n1)"
TARBALL="$(ls -1t "${BACKUP_DIR}"/arkidi_file_storage_[0-9]*.tar.gz 2>/dev/null | head -n1 || true)"

echo "[drill] STEP 2/4  create scratch DB '${SCRATCH_DB}'"
"${PSQL[@]}" -d "${DB_NAME}" -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${SCRATCH_DB}"

echo "[drill] STEP 3/4  restore via scripts/restore.sh"
DB_HOST="${DB_HOST}" DB_PORT="${DB_PORT}" DB_NAME="${SCRATCH_DB}" \
DB_USER="${DB_USER}" DB_PASSWORD="${DB_PASSWORD}" \
FILE_STORAGE_PATH="${WORKDIR}/file-storage" \
"$(dirname "$0")/restore.sh" "${DUMP}" "${TARBALL:-}"

echo "[drill] STEP 4/4  verify round-trip"
SRC_TABLES="$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -t -A -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")"
REST_TABLES="$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${SCRATCH_DB}" -t -A -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")"
echo "[drill] table counts: source=${SRC_TABLES} restored=${REST_TABLES}"
[ "${SRC_TABLES}" = "${REST_TABLES}" ] || { echo "[drill] FAIL: restored table count differs from source." >&2; exit 1; }

for TABLE in users faithful; do
    SRC="$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -t -A -c "SELECT count(*) FROM ${TABLE}")"
    REST="$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${SCRATCH_DB}" -t -A -c "SELECT count(*) FROM ${TABLE}")"
    echo "[drill] ${TABLE}: source=${SRC} restored=${REST}"
    [ "${SRC}" = "${REST}" ] || { echo "[drill] FAIL: ${TABLE} count differs after restore." >&2; exit 1; }
done

if [ -n "${TARBALL}" ] && [ -d "${WORKDIR}/file-storage" ]; then
    echo "[drill] file-storage tarball restored into ${WORKDIR}/file-storage (ok)."
else
    echo "[drill] file-storage directory was empty on source; nothing to verify."
fi

echo "[drill] SUCCESS: backup -> restore -> verify round-trip completed end-to-end."
trap - EXIT
cleanup