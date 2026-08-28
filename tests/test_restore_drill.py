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
            "-h", settings.DATABASE_HOST,
            "-p", str(settings.DATABASE_PORT),
            "-U", settings.DATABASE_USER,
            "-d", settings.DATABASE_NAME,
            "-t", "-A",
            "-c", "SELECT rolcreatedb FROM pg_roles WHERE rolname = current_user",
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
            "-h", settings.DATABASE_HOST,
            "-p", str(settings.DATABASE_PORT),
            "-U", settings.DATABASE_USER,
            "-d", settings.DATABASE_NAME,
            "-t", "-A",
            "-c", "SELECT 1",
        ],
        env=_env(settings.DATABASE_NAME),
    )
    return res.returncode == 0 and res.stdout.strip() == "1"


def _psql_count(tools: dict, database: str, table: str):
    res = _run(
        [
            tools["psql"],
            "-h", settings.DATABASE_HOST,
            "-p", str(settings.DATABASE_PORT),
            "-U", settings.DATABASE_USER,
            "-d", database,
            "-t", "-A",
            "-c", f"SELECT count(*) FROM {table}",
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
            "-h", settings.DATABASE_HOST,
            "-p", str(settings.DATABASE_PORT),
            "-U", settings.DATABASE_USER,
            "-d", database,
            "-t", "-A",
            "-c",
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'",
        ],
        env=_env(database),
    )
    if res.returncode != 0:
        raise AssertionError(f"table-count query failed on {database}: {res.stderr}")
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
                    "--no-owner", "--no-acl",
                    "-h", settings.DATABASE_HOST,
                    "-p", str(settings.DATABASE_PORT),
                    "-U", settings.DATABASE_USER,
                    "-d", settings.DATABASE_NAME,
                    "-Fc",
                    "-f", dump_path,
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
                    "-h", settings.DATABASE_HOST,
                    "-p", str(settings.DATABASE_PORT),
                    "-U", settings.DATABASE_USER,
                    "-d", settings.DATABASE_NAME,
                    "-c", f"CREATE DATABASE {scratch}",
                ],
                env=_env(settings.DATABASE_NAME),
            )
            assert createdb.returncode == 0, f"CREATE DATABASE failed: {createdb.stderr}"

            # --- 2b. Restore file-storage tarball; verify bytes round-trip ---
            restored_fs = os.path.join(workdir, "restored_file_storage")
            os.makedirs(restored_fs, exist_ok=True)
            with tarfile.open(files_tarball, "r:gz") as tar:
                tar.extractall(restored_fs)
            restored_probe = os.path.join(restored_fs, os.path.basename(tmp_file_storage), "probe.txt")
            assert os.path.exists(restored_probe), "file-storage probe not restored"
            with open(restored_probe, "rb") as fh:
                assert fh.read() == probe_bytes, "file-storage bytes did not round-trip"

            # --- 3. Restore into scratch (mirrors restore.sh flags) ---
            restore_res = _run(
                [
                    tools["pg_restore"],
                    "--no-owner", "--no-acl", "--clean", "--if-exists",
                    "-h", settings.DATABASE_HOST,
                    "-p", str(settings.DATABASE_PORT),
                    "-U", settings.DATABASE_USER,
                    "-d", scratch,
                    dump_path,
                ],
                env=_env(scratch),
            )
            assert restore_res.returncode == 0, f"pg_restore failed: {restore_res.stderr}"

            # --- 4. Verify: table graph + representative row counts match source ---
            src_tables = _table_count(tools, settings.DATABASE_NAME)
            restored_tables = _table_count(tools, scratch)
            assert restored_tables == src_tables, (
                f"restored table count {restored_tables} != source {src_tables}"
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
                    "-h", settings.DATABASE_HOST,
                    "-p", str(settings.DATABASE_PORT),
                    "-U", settings.DATABASE_USER,
                    "-d", settings.DATABASE_NAME,
                    "-c",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    f"WHERE datname = '{scratch}' AND pid <> pg_backend_pid()",
                ],
                env=_env(settings.DATABASE_NAME),
            )
            _run(
                [
                    tools["psql"],
                    "-h", settings.DATABASE_HOST,
                    "-p", str(settings.DATABASE_PORT),
                    "-U", settings.DATABASE_USER,
                    "-d", settings.DATABASE_NAME,
                    "-c", f"DROP DATABASE IF EXISTS {scratch}",
                ],
                env=_env(settings.DATABASE_NAME),
            )