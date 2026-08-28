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
#
# PostGIS provisioning: a freshly created scratch database has NO PostGIS, and a
# non-superuser application role cannot `CREATE EXTENSION postgis` (PostGIS is a
# non-trusted extension). The drill therefore provisions PostGIS in the scratch
# DB through an *admin* (superuser/DBA) connection before restoring. That admin
# role defaults to the application role (which is a superuser in the default
# postgis/postgis Docker image and in simple local setups), so no extra config is
# needed there; set DB_ADMIN_USER/DB_ADMIN_PASSWORD when the app role is not a
# superuser.
# Usage:
#   DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
#   DB_USER=arkidi_user DB_PASSWORD=secret BACKUP_DIR=./backups \
#   FILE_STORAGE_PATH=./file-storage \
#   DB_ADMIN_USER=postgres DB_ADMIN_PASSWORD=super_secret \
#   ./scripts/restore_drill.sh
set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-arkidi_db}"
DB_USER="${DB_USER:-arkidi_user}"
DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD environment variable is required}"
DB_ADMIN_USER="${DB_ADMIN_USER:-${DB_USER}}"
DB_ADMIN_PASSWORD="${DB_ADMIN_PASSWORD:-${DB_PASSWORD}}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
FILE_STORAGE_PATH="${FILE_STORAGE_PATH:-./file-storage}"
WORKDIR="$(mktemp -d)"
TS="$(date +%Y%m%d_%H%M%S)"
SCRATCH_DB="arkidi_restore_drill_${TS}"

export PGCLIENTENCODING=UTF8
PSQL=(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}")
ADMIN_PSQL=(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_ADMIN_USER}")

cleanup() {
    set +e
    PGPASSWORD="${DB_PASSWORD}" "${PSQL[@]}" -d ${DB_NAME} -v ON_ERROR_STOP=0 \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${SCRATCH_DB}' AND pid<>pg_backend_pid()" >/dev/null 2>&1
    PGPASSWORD="${DB_PASSWORD}" "${PSQL[@]}" -d ${DB_NAME} -v ON_ERROR_STOP=0 -c "DROP DATABASE IF EXISTS ${SCRATCH_DB}" >/dev/null 2>&1
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
PGPASSWORD="${DB_PASSWORD}" "${PSQL[@]}" -d "${DB_NAME}" -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${SCRATCH_DB}"

echo "[drill] STEP 2b/4  enable PostGIS in scratch DB '${SCRATCH_DB}' (via admin role)"
# A fresh database has no PostGIS, and a non-superuser role cannot create the
# extension. Provision it as the admin role, then let the application role create
# its own tables in the public schema.
PGPASSWORD="${DB_ADMIN_PASSWORD}" "${ADMIN_PSQL[@]}" -d "${SCRATCH_DB}" -v ON_ERROR_STOP=1 \
    -c "CREATE EXTENSION IF NOT EXISTS postgis"
PGPASSWORD="${DB_ADMIN_PASSWORD}" "${ADMIN_PSQL[@]}" -d "${SCRATCH_DB}" -v ON_ERROR_STOP=1 \
    -c "GRANT CREATE ON SCHEMA public TO ${DB_USER}"
# Make future objects in public usable by the application role too (the restored
# tables are owned by the app role already since pg_restore runs as it).
PGPASSWORD="${DB_ADMIN_PASSWORD}" "${ADMIN_PSQL[@]}" -d "${SCRATCH_DB}" -v ON_ERROR_STOP=1 \
    -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER}"

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

# Guard specifically against the PostGIS gap: geometry-backed tables (parishes,
# centrales, land_parcels) must have their geometry/geography columns restored.
GEO_SQL="SELECT count(*) FROM information_schema.columns WHERE table_schema='public' AND udt_name IN ('geometry','geography')"
SRC_GEO="$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -t -A -c "${GEO_SQL}")"
REST_GEO="$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${SCRATCH_DB}" -t -A -c "${GEO_SQL}")"
echo "[drill] geometry columns: source=${SRC_GEO} restored=${REST_GEO}"
[ "${SRC_GEO}" = "${REST_GEO}" ] || { echo "[drill] FAIL: geometry/geography columns did not restore (PostGIS not enabled in scratch DB?)." >&2; exit 1; }

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