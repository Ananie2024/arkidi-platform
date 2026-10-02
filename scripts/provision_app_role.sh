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
#   * no CREATEDB privilege: the restore drill uses the dedicated DBA role to
#     create and drop its isolated scratch database.
#
# Run it as an admin/superuser (the role itself is NOT a superuser):
#
#   DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
#   DB_ADMIN_USER=postgres DB_ADMIN_PASSWORD=secret \
#   APP_ROLE=arkidi_app APP_ROLE_PASSWORD=secret \
#   ./scripts/provision_app_role.sh
#
# Afterwards point the app at the new role and set DB_ADMIN_USER/DB_ADMIN_PASSWORD
# for the restore drill's scratch-database and PostGIS provisioning operations.
set -euo pipefail

DB_HOST="${DB_HOST:-${DATABASE_HOST:-localhost}}"
DB_PORT="${DB_PORT:-${DATABASE_PORT:-5432}}"
DB_NAME="${DB_NAME:-${DATABASE_NAME:-arkidi_db}}"
DB_ADMIN_USER="${DB_ADMIN_USER:?DB_ADMIN_USER (superuser/DBA) is required}"
DB_ADMIN_PASSWORD="${DB_ADMIN_PASSWORD:?DB_ADMIN_PASSWORD is required}"
APP_ROLE="${APP_ROLE:-${DATABASE_USER:-arkidi_app}}"
APP_ROLE_PASSWORD="${APP_ROLE_PASSWORD:-${DATABASE_PASSWORD:?APP_ROLE_PASSWORD or DATABASE_PASSWORD is required}}"

if [ "${APP_ROLE}" = "${DB_ADMIN_USER}" ]; then
    echo "[provision] Refusing to use the DBA role as the application role." >&2
    exit 2
fi

echo "[provision] Creating/refreshing non-superuser role '${APP_ROLE}' on ${DB_NAME}@${DB_HOST}:${DB_PORT} ..."

ROLE_EXISTS="$(PGPASSWORD="${DB_ADMIN_PASSWORD}" psql \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_ADMIN_USER}" -d "${DB_NAME}" \
    -v app_role="${APP_ROLE}" -t -A -c "SELECT 1 FROM pg_roles WHERE rolname = :'app_role'")"
if [ -z "${ROLE_EXISTS}" ]; then
    echo "[provision] Role '${APP_ROLE}' does not exist; creating it (NON-superuser)."
    PGPASSWORD="${DB_ADMIN_PASSWORD}" psql \
        -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_ADMIN_USER}" -d "${DB_NAME}" \
        -v ON_ERROR_STOP=1 -v app_role="${APP_ROLE}" -v app_password="${APP_ROLE_PASSWORD}" <<'SQL'
CREATE ROLE :"app_role" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD :'app_password';
SQL
else
    echo "[provision] Role '${APP_ROLE}' already exists; refreshing its login and password."
    PGPASSWORD="${DB_ADMIN_PASSWORD}" psql \
        -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_ADMIN_USER}" -d "${DB_NAME}" \
        -v ON_ERROR_STOP=1 -v app_role="${APP_ROLE}" -v app_password="${APP_ROLE_PASSWORD}" <<'SQL'
ALTER ROLE :"app_role" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD :'app_password';
SQL
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
    -v app_role="${APP_ROLE}" -t -A -c "SELECT 'rolname=' || rolname || ' rolsuper=' || rolsuper || ' rolcreatedb=' || rolcreatedb FROM pg_roles WHERE rolname = :'app_role'"
echo "[provision] Done."

