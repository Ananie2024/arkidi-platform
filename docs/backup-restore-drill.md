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

### Automated test

`tests/test_restore_drill.py` runs the same sequence in CI/local (and is the
same proof the shell drill performs). It is skipped gracefully when the tools,
DB, or the `CREATEDB` privilege are absent (e.g. a CI job without Postgres):

```bash
python -m pytest tests/test_restore_drill.py
```

## What the drill verifies

1. `pg_dump` on the source database produces a non-empty dump.
2. The file-storage tarball restores with byte-for-byte identical content.
3. `pg_restore --no-owner --no-acl --clean --if-exists` populates the scratch DB.
4. The restored schema's public-table count equals the source's table count.
5. Representative row counts (`users`, `faithful`) match between source and
   restored database.

If any of those fail the drill exits non-zero and reports which step failed.