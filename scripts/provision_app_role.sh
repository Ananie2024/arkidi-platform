#!/usr/bin/env bash
# Arkidi Platform – provision / refresh a NON-superuser application database role.
#
# By default the official postgis/postgis Docker image and simple local setups
# give the application role superuser rights. A real production deployment should
# NOT do that: the app should run under a least-privilege role. This script
# creates (idempotently) such a role and grants exactly the privileges the app
# needs to run migrations, the API, and the backup/restore drill:
#
#   * CONNECT on the database
#   * CREATE + USAGE on the public schema (so `alembic upgrade head` and a
#     restore can create the app's own tables)
#   * default privileges so the role can read/write what it creates
#   * CREATEDB (required by scripts/restore_drill.sh to create its scratch DB)
#
# Run it as an admin/superuser (the role itself is NOT a superuser):
#
#   DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
#   DB_ADMIN_USER=postgres DB_ADMIN_PASSWORD=secret \
#   APP_ROLE=arkidi_app APP_ROLE_PASSWORD=secret \
#   ./scripts/provision_app_role.sh
#
# Afterwards point the app at the new role and, for the restore drill, also set
# DB_ADMIN_USER=postgres DB_ADMIN_PASSWORD=secret so the drill can provision
# PostGIS in its scratch database (a non-superuser cannot CREATE EXTENSION).
set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-arkidi_db}"
DB_ADMIN_USER="${DB_ADMIN_USER:?DB_ADMIN_USER (superuser/DBA) is required}"
DB_ADMIN_PASSWORD="${DB_ADMIN_PASSWORD:?DB_ADMIN_PASSWORD is required}"
APP_ROLE="${APP_ROLE:-arkidi_app}"
APP_ROLE_PASSWORD="${APP_ROLE_PASSWORD:?APP_ROLE_PASSWORD is required}"

echo "[provision] Creating/refreshing non-superuser role '${APP_ROLE}' on ${DB_NAME}@${DB_HOST}:${DB_PORT} ..."

ROLE_EXISTS="$(PGPASSWORD="${DB_ADMIN_PASSWORD}" psql \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_ADMIN_USER}" -d "${DB_NAME}" \
    -t -A -c "SELECT 1 FROM pg_roles WHERE rolname = '${APP_ROLE}'")"
if [ -z "${ROLE_EXISTS}" ]; then
    echo "[provision] Role '${APP_ROLE}' does not exist; creating it (NON-superuser)."
    PGPASSWORD="${DB_ADMIN_PASSWORD}" psql \
        -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_ADMIN_USER}" -d "${DB_NAME}" \
        -v ON_ERROR_STOP=1 \
        -c "CREATE ROLE \"${APP_ROLE}\" LOGIN NOSUPERUSER NOCREATEROLE CREATEDB PASSWORD '${APP_ROLE_PASSWORD}'"
else
    echo "[provision] Role '${APP_ROLE}' already exists; leaving attributes unchanged."
fi

# The GRANTs below use psql variables (substituted BEFORE execution); they must
# not live inside a dollar-quoted block, where psql does not interpolate.
PGPASSWORD="${DB_ADMIN_PASSWORD}" psql \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_ADMIN_USER}" -d "${DB_NAME}" \
    -v ON_ERROR_STOP=1 \
    -v app_role="${APP_ROLE}" \
    -v app_db="${DB_NAME}" <<'SQL'
GRANT CONNECT ON DATABASE :"app_db" TO :"app_role";
GRANT CREATE, USAGE ON SCHEMA public TO :"app_role";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO :"app_role";
SQL

echo "[provision] Verifying role is NOT a superuser:"
PGPASSWORD="${DB_ADMIN_PASSWORD}" psql \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_ADMIN_USER}" -d "${DB_NAME}" \
    -t -A -c "SELECT 'rolname=' || rolname || ' rolsuper=' || rolsuper || ' rolcreatedb=' || rolcreatedb FROM pg_roles WHERE rolname = '${APP_ROLE}'"
echo "[provision] Done."

