# Production Operations Runbook

This runbook covers the current Docker Compose production deployment. The
hosting provider, region, named on-call people, approved recovery objectives,
and cloud storage account are deployment decisions; record them before
production data is entered.

## Assign operational ownership

Name a primary and backup for each responsibility and test that they can
receive alerts:

| Responsibility | Suggested owner | Required action |
| --- | --- | --- |
| Application and host | Diocesan IT | Deployments, TLS, host monitoring, disk capacity, and incident coordination |
| Database and recovery | Named DBA or delegated IT operator | Database access, backups, restore authorization, and restore drills |
| Records and service impact | Chancellor / diocesan records lead | Decide service priorities and authorize recovery that may discard recent records |
| Alerts | Diocesan IT and named backup | Monitor backup, restore-drill, SMTP, and external health-check alerts |

Agree and record recovery point and recovery time objectives (RPO/RTO) with
these owners. The current nightly schedule implies up to roughly one day of
database changes could be lost if only the last completed dump is available;
it does not itself establish an approved RPO.

## Prepare the production environment

1. Choose the host and region, DNS name, storage provider, TLS certificate
   renewal process, and external health-monitoring service. Set `SERVER_NAME`,
   `PUBLIC_FRONTEND_URL`, `CORS_ORIGINS`, `SSL_CERT_PATH`, and `SSL_KEY_PATH`
   to those deployment values.
2. Copy `.env.production.example` to `.env.production` on the deployment host.
   Set unique strong secrets there; never commit that file or cloud credentials.
   The root `.env.production` and `secrets/` directory are ignored by Git.
3. Keep `POSTGRES_USER`/`POSTGRES_PASSWORD` as the PostgreSQL bootstrap DBA
   credentials for the Compose database. Set distinct `DATABASE_USER` and
   `DATABASE_PASSWORD` values for the application. The one-shot `database-init`
   service provisions that account as a non-superuser without `CREATEDB` before
   the API runs migrations. `DATABASE_ADMIN_USER`/`DATABASE_ADMIN_PASSWORD`
   default to the bootstrap DBA and are used by the backup worker for its
   scratch-database restore drill; set them to an appropriately privileged DBA
   account if needed. Restrict DBA credentials to the database initializer and
   backup worker, and rotate them under the diocesan credential policy. The
   current production overlay targets its internal Compose database. If adapting
   it for an external managed database, override that host and arrange equivalent
   application-role provisioning with its DBA before deployment.
4. Configure at least one offsite destination for production. For GCS, set
   `GCS_ENABLED=true`, project and bucket values, and place the service account
   key at `secrets/gcs-key.json` (or configure workload identity and leave the
   credentials path empty). For B2, set its enabled flag, account ID, key, and
   bucket. The Celery worker receives the cloud credentials; the API container
   does not. Enable provider-side encryption and a lifecycle/retention rule for
   the bucket. Local retention is controlled by `BACKUP_KEEP_DAYS` (1 to 3650,
   default 14); cloud retention is controlled by that provider lifecycle rule.
5. Configure working SMTP credentials, `EMAIL_SENDER`, and comma-separated
   `ALERT_RECIPIENTS`. The recipients must be monitored by named operators.
   Without working SMTP and recipients, failures are only written to container
   logs and can be missed.
6. Agree who can authorize a production restore and who validates restored
   canonical and financial records. Use encrypted host storage and limit access
   to the backup volume and uploaded files; both contain sensitive records.

Validate the merged Compose configuration without printing interpolated
secrets:

```bash
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml config --quiet
```

The database initializer waits for PostgreSQL, and the API waits for its
successful completion before running migrations. The backup worker and
scheduler wait for the API health check. Run exactly one Celery Beat instance
so scheduled backups and drills are not duplicated.

## Deploy and verify

Before each release, confirm a recent backup completed and its database dump
and file-storage archive reached the configured offsite destination. Review
the migration files included in the release and confirm the current production
database version and available disk space. The API entrypoint runs
`alembic upgrade head` automatically before it becomes healthy; the worker and
scheduler do not run migrations.

Deploy with the Compose command in the README. Then verify:

```bash
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml logs --since=15m backend celery-worker celery-beat
```

Confirm the external monitor can reach `https://<SERVER_NAME>/health`, that the
response is healthy, and that staff can complete a small approved workflow.
The health route checks PostgreSQL and Redis. Also confirm that Celery Beat and
the worker are running and that alert email reaches the configured recipients.

## Backup and alert operations

- Nightly database and file-storage backups run at 01:30 Africa/Kigali.
- A restore drill runs every Sunday at 03:30 Africa/Kigali. It creates a
  scratch database, restores and compares representative schema/data and file
  storage, then drops the scratch database.
- Failed database dumps, enabled offsite uploads, or restore drills cause the
  scheduled task to log and send an alert. Cloud upload errors are failures;
  the backup job must not report success when an enabled destination is down.
- Local generated dump and file archive files older than `BACKUP_KEEP_DAYS` are
  pruned after the new backup and any enabled offsite uploads succeed. Provider
  lifecycle policies independently govern offsite retention.
- Monitor host disk capacity and cloud quota. A full backup volume can prevent
  the next dump from completing. Review worker and scheduler logs after alerts.

The host-local backup volume is not an offsite copy. If the host is lost, use
the cloud copy or another separately managed replica. Keep the deployment
configuration and recovery instructions available to the recovery team without
including production secrets.

## Restore and incident recovery

1. Open an incident, notify the named IT, DBA, and records owners, and record
   the approved recovery point. Stop API writes and scheduled/background jobs
   before a cutover so records do not diverge during recovery.
2. Identify a matching database dump and file-storage archive from the same
   backup timestamp. Verify the dump is readable with `pg_restore --list` and
   verify the archive with `tar -tzf`. Do not extract an untrusted archive.
3. Prefer restoring to a new, isolated database and storage directory. Provision
   PostgreSQL and PostGIS first, then use `scripts/restore.sh` with the matching
   database dump and file-storage archive. The restore script cleans objects in
   its target database; never point it at the only production database unless
   the incident commander explicitly authorizes that recovery path.
4. Run application migrations only after the restore is verified and the
   recovery owner approves the target schema. Validate table and geography
   counts, representative users and faithful records, uploaded document access,
   login, and the agreed critical staff workflows.
5. Point the service at the recovered database and storage, bring up the API,
   worker, scheduler, and frontend, then check `/health`, logs, and external
   monitoring. Record the recovered backup timestamp and any data loss against
   the agreed RPO. Keep the original source and backup artifacts until the
   records owner signs off.

## Migration rollback and application rollback

Do not assume an Alembic downgrade can safely reverse production data changes.
Review each migration's `downgrade()` and data effects before release. Prefer
backward-compatible expand-and-contract migrations so the previous application
image can run briefly against the upgraded schema. If a migration is not
reversible or data was transformed, roll forward with a corrective release or
restore the pre-deployment database and matching files into a separate target;
restoring over live data requires explicit incident authorization. Keep the
previous image/version identifier and the pre-deploy backup timestamp in the
release record.
