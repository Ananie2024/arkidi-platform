# Backup & Restore Drill

## Why a drill exists

A backup is only as good as your ability to restore it. Arkidi used to document
`scripts/backup.sh` and `scripts/restore.sh` but a restore had never actually
been exercised, so a real recovery could have failed at the exact moment it was
needed. To prove the whole path works we added an end-to-end drill and an
automated test.

## Coverage

`scripts/backup.sh` now produces **two** artifacts in `BACKUP_DIR`
(default `./backups`):

| Artifact | Content |
| --- | --- |
| `arkidi_<TS>.dump` | `pg_dump` custom-format snapshot of the PostgreSQL/PostGIS database |
| `arkidi_file_storage_<TS>.tar.gz` | tarball of `FILE_STORAGE_PATH` (default `./file-storage`) — uploaded documents, photos, scanned canonical registers |

`scripts/restore.sh` restores the `.dump` (into `DB_NAME`) and optionally the
file-storage tarball (second CLI argument) into `FILE_STORAGE_PATH`.

## Running a restore drill

The drill backs up the real database, restores into a throwaway scratch
database, verifies the round-trip, then drops the scratch database. It never
touches the live data.

```bash
DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
DB_USER=arkidi_user DB_PASSWORD=secret \
./scripts/restore_drill.sh
```

You can also control the backup/filestorage locations:

```bash
BACKUP_DIR=./backups FILE_STORAGE_PATH=./file-storage \
DB_PASSWORD=secret ./scripts/restore_drill.sh
```

### Requirements

- `psql`, `pg_dump`, `pg_restore`, `tar` on `PATH`
- The configured DB role must have the `CREATEDB` privilege (to create the
  scratch database). `arkidi_user` has it by default.
- An **admin** (superuser/DBA) role able to provision the PostGIS extension. In
  the default postgis/postgis Docker image `POSTGRES_USER` is a superuser, so
  `DB_ADMIN_USER`/`DB_ADMIN_PASSWORD` default to the application credentials and
  no extra configuration is needed. For a non-superuser application role, point
  them at the DBA account (e.g. the container's `postgres`), e.g.:

  ```bash
  DB_HOST=localhost DB_PORT=5432 DB_NAME=arkidi_db \
  DB_USER=arkidi_app DB_PASSWORD=secret \
  DB_ADMIN_USER=postgres DB_ADMIN_PASSWORD=dba_secret \
  ./scripts/restore_drill.sh
  ```

### Why PostGIS must be provisioned separately

A freshly created scratch database has **no PostGIS**, and the drill restores
geometry-backed tables (`parishes`, `centrales`, `land_parcels`). Enabling
PostGIS in the scratch DB is not something a non-superuser application role can
do on its own — PostGIS is a *non-trusted* extension, so `CREATE EXTENSION
postgis` requires a superuser (or a role the DBA has explicitly granted). The
drill therefore provisions PostGIS in the scratch DB through the admin role
before restoring, exactly as a DBA would provision the extension in a real
deployment.

The restore itself (`scripts/restore.sh`) then deliberately skips the
PostGIS-infrastructure entries that `pg_dump` records (`CREATE`/`COMMENT ON` the
`postgis` extension and the `spatial_ref_sys` table), because those are owned by
the extension and cannot be created or written by the application role. Without
this separation the previously-seen failure happens:

```text
pg_restore: error: could not execute query: ERROR:  permission denied to create extension "postgis"
```

This is exactly the bug the drill used to hide: in CI the official image's
default `POSTGRES_USER` is a superuser, so `pg_restore` could silently create the
extension and mask the production-realistic failure. CI and this drill now run
migrations, the test suite, and the restore under a genuinely **non-superuser**
application role so the gap cannot hide again.

### Automated test

`tests/test_restore_drill.py` runs the same sequence in CI/local (and is the
same proof the shell drill performs). It is skipped gracefully when the tools,
DB, or the `CREATEDB` privilege are absent (e.g. a CI job without Postgres). When
`DATABASE_ADMIN_USER`/`DATABASE_ADMIN_PASSWORD` are set (non-superuser setup)
the test provisions PostGIS through those; otherwise it falls back to the
application role (superuser case):

```bash
python -m pytest tests/test_restore_drill.py
```

### Non-superuser local setup

To run the whole suite (and the drill) locally under a real non-superuser role,
provision the role once with the helper, then point the app at it:

```bash
DB_ADMIN_USER=postgres DB_ADMIN_PASSWORD=secret \
APP_ROLE=arkidi_app APP_ROLE_PASSWORD=secret \
./scripts/provision_app_role.sh   # role is NOT a superuser

# then in .env:
# DATABASE_USER=arkidi_app
# DATABASE_PASSWORD=secret
# DATABASE_ADMIN_USER=postgres
# DATABASE_ADMIN_PASSWORD=secret
```

## What the drill verifies

1. `pg_dump` on the source database produces a non-empty dump.
2. The file-storage tarball restores with byte-for-byte identical content.
3. `pg_restore --no-owner --no-acl --clean --if-exists` populates the scratch DB.
4. The restored schema's public-table count equals the source's table count.
5. The restored schema's geometry/geography column count equals the source's
   (guards the PostGIS-in-restore gap: `parishes`, `centrales`, `land_parcels`).
6. Representative row counts (`users`, `faithful`) match between source and
   restored database.

If any of those fail the drill exits non-zero and reports which step failed.