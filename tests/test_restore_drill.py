"""
End-to-end restore drill test.

Proves that a backup taken by the same pg_dump/pg_restore commands wrapped by
``scripts/backup.sh`` / ``scripts/restore.sh`` can actually be restored into a
fresh database and that data round-trips (this is the exact claim of the
``scripts/restore_drill.sh`` shell drill). It runs against the *live* database
configured in ``.env`` but never modifies it -- it restores into a throwaway
scratch database which is dropped afterwards.

The test is skipped when the required Postgres client tools are unavailable,
when the configured DB role lacks the ``CREATEDB`` privilege, or when the source
database is unreachable (e.g. local CI without a Postgres service).

A freshly created scratch database has no PostGIS, and a non-superuser
application role cannot ``CREATE EXTENSION postgis`` (it is a non-trusted
extension). The test therefore provisions PostGIS in the scratch DB through the
privileged admin role (``DATABASE_ADMIN_USER``/``DATABASE_ADMIN_PASSWORD``,
defaulting to the application role when that role is a superuser) and restores
with a filtered ``--use-list`` that skips the PostGIS-infrastructure TOC entries.
This exercises the production-realistic non-superuser path so the bug this test
guards (geometry-backed tables failing to restore) cannot hide behind a
superuser Docker-image default again.
"""

import os
import shutil
import subprocess
import tarfile
import tempfile
import uuid

import pytest

from app.config import settings

PG_TOOLS = ["pg_dump", "pg_restore", "psql", "tar"]


def _find_tools():
    return {tool: shutil.which(tool) for tool in PG_TOOLS}


def _env(database: str) -> dict:
    env = os.environ.copy()
    env["PGPASSWORD"] = settings.DATABASE_PASSWORD
    env["PGCLIENTENCODING"] = "UTF8"
    return env


def _env_admin(database: str) -> dict:
    """Env using the privileged admin role (defaults to the app role)."""
    env = os.environ.copy()
    env["PGPASSWORD"] = settings.effective_admin_password
    env["PGCLIENTENCODING"] = "UTF8"
    return env


def _run(cmd, cwd=None, env=None, check=False):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
        check=check,
    )


def _can_create_database(tools: dict) -> bool:
    res = _run(
        [
            tools["psql"],
            "-h",
            settings.DATABASE_HOST,
            "-p",
            str(settings.DATABASE_PORT),
            "-U",
            settings.DATABASE_USER,
            "-d",
            settings.DATABASE_NAME,
            "-t",
            "-A",
            "-c",
            "SELECT rolcreatedb FROM pg_roles WHERE rolname = current_user",
        ],
        env=_env(settings.DATABASE_NAME),
    )
    if res.returncode != 0:
        return False
    return res.stdout.strip().lower() == "t"


def _reached_database(tools: dict) -> bool:
    res = _run(
        [
            tools["psql"],
            "-h",
            settings.DATABASE_HOST,
            "-p",
            str(settings.DATABASE_PORT),
            "-U",
            settings.DATABASE_USER,
            "-d",
            settings.DATABASE_NAME,
            "-t",
            "-A",
            "-c",
            "SELECT 1",
        ],
        env=_env(settings.DATABASE_NAME),
    )
    return res.returncode == 0 and res.stdout.strip() == "1"


def _psql_count(tools: dict, database: str, table: str):
    res = _run(
        [
            tools["psql"],
            "-h",
            settings.DATABASE_HOST,
            "-p",
            str(settings.DATABASE_PORT),
            "-U",
            settings.DATABASE_USER,
            "-d",
            database,
            "-t",
            "-A",
            "-c",
            f"SELECT count(*) FROM {table}",
        ],
        env=_env(database),
    )
    if res.returncode != 0:
        raise AssertionError(f"count query failed on {database}.{table}: {res.stderr}")
    return int(res.stdout.strip())


def _table_count(tools: dict, database: str) -> int:
    res = _run(
        [
            tools["psql"],
            "-h",
            settings.DATABASE_HOST,
            "-p",
            str(settings.DATABASE_PORT),
            "-U",
            settings.DATABASE_USER,
            "-d",
            database,
            "-t",
            "-A",
            "-c",
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'",
        ],
        env=_env(database),
    )
    if res.returncode != 0:
        raise AssertionError(f"table-count query failed on {database}: {res.stderr}")
    return int(res.stdout.strip())


def _geometry_count(tools: dict, database: str) -> int:
    """Count geometry/geography columns — guards the PostGIS-in-restore gap."""
    res = _run(
        [
            tools["psql"],
            "-h",
            settings.DATABASE_HOST,
            "-p",
            str(settings.DATABASE_PORT),
            "-U",
            settings.DATABASE_USER,
            "-d",
            database,
            "-t",
            "-A",
            "-c",
            "SELECT count(*) FROM information_schema.columns "
            "WHERE table_schema = 'public' AND udt_name IN ('geometry', 'geography')",
        ],
        env=_env(database),
    )
    if res.returncode != 0:
        raise AssertionError(f"geometry-count query failed on {database}: {res.stderr}")
    return int(res.stdout.strip())


@pytest.mark.integration
def test_restore_drill_end_to_end():
    tools = _find_tools()
    missing = [name for name, path in tools.items() if not path]
    if missing:
        pytest.skip(f"Postgres client tools not found: {missing}")

    if not _reached_database(tools):
        pytest.skip("Source database is not reachable on localhost.")

    if not _can_create_database(tools):
        pytest.skip("Configured DB role lacks CREATEDB; cannot create a scratch DB.")

    scratch = f"arkidi_restore_drill_{uuid.uuid4().hex[:10]}"

    try:
        with tempfile.TemporaryDirectory() as workdir:
            dump_path = os.path.join(workdir, "arkidi_drill.dump")
            files_tarball = os.path.join(workdir, "arkidi_file_storage_drill.tar.gz")
            tmp_file_storage = os.path.join(workdir, "src_file_storage")
            probe_path = os.path.join(tmp_file_storage, "probe.txt")
            os.makedirs(tmp_file_storage, exist_ok=True)

            probe_bytes = b"RESTORE-DRILL-PROBE-%s" % uuid.uuid4().hex.encode()
            with open(probe_path, "wb") as fh:
                fh.write(probe_bytes)

            # --- 1. Backup: dump DB + archive file-storage (mirrors backup.sh) ---
            dump_res = _run(
                [
                    tools["pg_dump"],
                    "--no-owner",
                    "--no-acl",
                    "-h",
                    settings.DATABASE_HOST,
                    "-p",
                    str(settings.DATABASE_PORT),
                    "-U",
                    settings.DATABASE_USER,
                    "-d",
                    settings.DATABASE_NAME,
                    "-Fc",
                    "-f",
                    dump_path,
                ],
                env=_env(settings.DATABASE_NAME),
            )
            assert dump_res.returncode == 0, f"pg_dump failed: {dump_res.stderr}"
            assert os.path.getsize(dump_path) > 0, "pg_dump produced an empty dump"

            with tarfile.open(files_tarball, "w:gz") as tar:
                tar.add(tmp_file_storage, arcname=os.path.basename(tmp_file_storage))

            # --- 2. Create scratch database ---
            createdb = _run(
                [
                    tools["psql"],
                    "-h",
                    settings.DATABASE_HOST,
                    "-p",
                    str(settings.DATABASE_PORT),
                    "-U",
                    settings.DATABASE_USER,
                    "-d",
                    settings.DATABASE_NAME,
                    "-c",
                    f"CREATE DATABASE {scratch}",
                ],
                env=_env(settings.DATABASE_NAME),
            )
            assert createdb.returncode == 0, f"CREATE DATABASE failed: {createdb.stderr}"

            # --- 2a. Provision PostGIS in the scratch DB (via the admin role).
            # A freshly created DB has no PostGIS and a non-superuser app role
            # cannot `CREATE EXTENSION postgis`, so this uses the privileged
            # admin role (defaults to the app role when it is a superuser).
            provision = _run(
                [
                    tools["psql"],
                    "-h",
                    settings.DATABASE_HOST,
                    "-p",
                    str(settings.DATABASE_PORT),
                    "-U",
                    settings.effective_admin_user,
                    "-d",
                    scratch,
                    "-c",
                    "CREATE EXTENSION IF NOT EXISTS postgis",
                ],
                env=_env_admin(scratch),
            )
            assert provision.returncode == 0, f"CREATE EXTENSION postgis failed: {provision.stderr}"
            grant = _run(
                [
                    tools["psql"],
                    "-h",
                    settings.DATABASE_HOST,
                    "-p",
                    str(settings.DATABASE_PORT),
                    "-U",
                    settings.effective_admin_user,
                    "-d",
                    scratch,
                    "-c",
                    f"GRANT CREATE ON SCHEMA public TO {settings.DATABASE_USER}",
                ],
                env=_env_admin(scratch),
            )
            assert grant.returncode == 0, f"GRANT CREATE on public schema failed: {grant.stderr}"

            # --- 2b. Restore file-storage tarball; verify bytes round-trip ---
            restored_fs = os.path.join(workdir, "restored_file_storage")
            os.makedirs(restored_fs, exist_ok=True)
            with tarfile.open(files_tarball, "r:gz") as tar:
                tar.extractall(restored_fs)
            restored_probe = os.path.join(
                restored_fs, os.path.basename(tmp_file_storage), "probe.txt"
            )
            assert os.path.exists(restored_probe), "file-storage probe not restored"
            with open(restored_probe, "rb") as fh:
                assert fh.read() == probe_bytes, "file-storage bytes did not round-trip"

            # --- 3. Restore into scratch (mirrors restore.sh) ---
            # Build a filtered pg_restore list so the PostGIS-infrastructure TOC
            # entries (CREATE/COMMENT ON the postgis extension and the
            # spatial_ref_sys COPY) are skipped; those are owned by PostGIS and
            # cannot be written by a non-superuser application role.
            list_path = os.path.join(workdir, "restore.list")
            filtered_list_path = os.path.join(workdir, "restore.filtered.list")
            list_res = _run(
                [tools["pg_restore"], "--list", "-f", list_path, dump_path],
                env=_env(scratch),
            )
            assert list_res.returncode == 0, f"pg_restore --list failed: {list_res.stderr}"
            with open(list_path, encoding="utf-8", errors="replace") as fh:
                entries = [
                    ln
                    for ln in fh
                    if ln.strip()
                    and "postgis" not in ln.lower()
                    and "spatial_ref_sys" not in ln.lower()
                ]
            with open(filtered_list_path, "w", encoding="utf-8") as fh:
                fh.writelines(entries)
            restore_res = _run(
                [
                    tools["pg_restore"],
                    "--no-owner",
                    "--no-acl",
                    "--clean",
                    "--if-exists",
                    "--use-list",
                    filtered_list_path,
                    "-h",
                    settings.DATABASE_HOST,
                    "-p",
                    str(settings.DATABASE_PORT),
                    "-U",
                    settings.DATABASE_USER,
                    "-d",
                    scratch,
                    dump_path,
                ],
                env=_env(scratch),
            )
            assert restore_res.returncode == 0, f"pg_restore failed: {restore_res.stderr}"

            # --- 4. Verify: table graph + geometry columns + row counts match ---
            src_tables = _table_count(tools, settings.DATABASE_NAME)
            restored_tables = _table_count(tools, scratch)
            assert (
                restored_tables == src_tables
            ), f"restored table count {restored_tables} != source {src_tables}"

            # Guard the PostGIS gap: geometry-backed tables must have restored columns.
            src_geo = _geometry_count(tools, settings.DATABASE_NAME)
            restored_geo = _geometry_count(tools, scratch)
            assert restored_geo == src_geo and restored_geo > 0, (
                f"geometry columns did not restore (source={src_geo}, restored={restored_geo}); "
                "PostGIS was not enabled in the scratch DB."
            )

            for table in ("users", "faithful"):
                src = _psql_count(tools, settings.DATABASE_NAME, table)
                restored = _psql_count(tools, scratch, table)
                assert restored == src, f"{table}: restored count {restored} != source {src}"

    finally:
        if scratch and _reached_database(tools):
            _run(
                [
                    tools["psql"],
                    "-h",
                    settings.DATABASE_HOST,
                    "-p",
                    str(settings.DATABASE_PORT),
                    "-U",
                    settings.DATABASE_USER,
                    "-d",
                    settings.DATABASE_NAME,
                    "-c",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    f"WHERE datname = '{scratch}' AND pid <> pg_backend_pid()",
                ],
                env=_env(settings.DATABASE_NAME),
            )
            _run(
                [
                    tools["psql"],
                    "-h",
                    settings.DATABASE_HOST,
                    "-p",
                    str(settings.DATABASE_PORT),
                    "-U",
                    settings.DATABASE_USER,
                    "-d",
                    settings.DATABASE_NAME,
                    "-c",
                    f"DROP DATABASE IF EXISTS {scratch}",
                ],
                env=_env(settings.DATABASE_NAME),
            )
