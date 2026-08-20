#!/usr/bin/env bash
#
# Arkidi Platform — Backend container entrypoint.
#
# Responsibilities, in order:
#   1. Wait (with bounded retries — not an infinite loop) for PostgreSQL to accept
#      connections. The backend starts in the same deployment as `postgres`, and
#      a hard `depends_on: condition: service_healthy` in docker-compose is a
#      first gate, but we still guard here so a slower DB cold-start does not
#      take the API process down during startup.
#   2. Run `alembic upgrade head` so the schema is applied automatically before
#      the process starts, with no manual alembic invocation required. This is
#      skipped for the celery worker/beat services (RUN_MIGRATIONS=false) so the
#      three processes do not race on DDL during a cold start.
#   3. exec the real process command so it inherits the PID and OS signals.
#
set -euo pipefail

DB_MAX_ATTEMPTS="${DB_MAX_ATTEMPTS:-30}"
DB_RETRY_DELAY_SECONDS="${DB_RETRY_DELAY_SECONDS:-2}"
RUN_MIGRATIONS="${RUN_MIGRATIONS:-true}"

log() {
    echo "[docker-entrypoint] $*"
}

wait_for_database() {
    local attempts=0
    local connected=0

    # DATABASE_HOST / DATABASE_PORT are injected by docker-compose. Fall back to
    # the local-development defaults if they are not present.
    local db_host="${DATABASE_HOST:-localhost}"
    local db_port="${DATABASE_PORT:-5432}"

    log "Waiting for PostgreSQL at ${db_host}:${db_port} (up to ${DB_MAX_ATTEMPTS} attempts)..."

    while [ "${attempts}" -lt "${DB_MAX_ATTEMPTS}" ]; do
        if python -c "import socket,sys; s=socket.socket(); s.settimeout(3); s.connect((sys.argv[1], int(sys.argv[2]))); s.close(); sys.exit(0)" "${db_host}" "${db_port}" 2>/dev/null; then
            connected=1
            break
        fi
        attempts=$((attempts + 1))
        echo "PostgreSQL not reachable yet (attempt ${attempts}/${DB_MAX_ATTEMPTS}); retrying in ${DB_RETRY_DELAY_SECONDS}s..."
        sleep "${DB_RETRY_DELAY_SECONDS}"
    done

    if [ "${connected}" -ne 1 ]; then
        echo "ERROR: PostgreSQL did not become reachable within ${DB_MAX_ATTEMPTS} attempts. Aborting." >&2
        exit 1
    fi

    log "PostgreSQL is reachable."
}

run_migrations() {
    if [ "${RUN_MIGRATIONS}" != "true" ]; then
        log "Skipping migrations (RUN_MIGRATIONS!=true)."
        return
    fi
    log "Applying database migrations (alembic upgrade head)..."
    alembic upgrade head
    log "Migrations are up to date."
}

# Resolve the process command:
#   * If positional args were given (docker-compose `command:` override, e.g. the
#     celery worker/beat commands), they are appended to the ENTRYPOINT and take
#     precedence.
#   * Otherwise default to the FastAPI uvicorn command. In production
#     (ENVIRONMENT=production) we do NOT use --reload and honour BACKEND_WORKERS;
#     in development the default is a reload worker for DX.
if [ -n "${1:-}" ]; then
    command_args=("$@")
else
    workers="${BACKEND_WORKERS:-1}"
    if [ "${ENVIRONMENT:-development}" = "production" ]; then
        command_args=(uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${workers}")
    else
        command_args=(uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload)
    fi
fi

wait_for_database
run_migrations

log "Starting process: ${command_args[*]}"
exec "${command_args[@]}"