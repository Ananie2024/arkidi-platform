#!/usr/bin/env python3
"""
Cloud Backup Upload Helper
==========================

Called by ``scripts/backup.sh`` after a local pg_dump + file-storage tarball
has been created.  Uploads the resulting artefacts to Google Cloud Storage
(``google-cloud-storage``) or Backblaze B2 (``b2sdk``) when the matching
cloud provider is enabled in configuration.

Both SDKs are listed in ``requirements.txt`` but were previously dead
weight — this script is the code path that makes them real.

Usage (called from backup.sh):
    python3 scripts/cloud_upload.py <file_path> [--provider gcs|b2]

If neither provider is enabled, the script exits 0 (no-op) so backup.sh
can call it unconditionally.

Environment / settings (see app.config.Settings):
    GCS_ENABLED, GCS_PROJECT_ID, GCS_BUCKET_NAME, GCS_CREDENTIALS_PATH
    B2_ENABLED, B2_ACCOUNT_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME
"""
import os
import sys
import logging

from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("arkidi.cloud_upload")


def _upload_to_gcs(filepath: str) -> str:
    """Upload *filepath* to the configured GCS bucket and return the object name."""
    from google.cloud import storage  # imported lazily — only required when GCS is used

    if not settings.GCS_BUCKET_NAME:
        raise RuntimeError("GCS_BUCKET_NAME is not set")

    credentials = settings.GCS_CREDENTIALS_PATH
    if credentials and os.path.isfile(credentials):
        client = storage.Client.from_service_account_json(credentials)
    else:
        client = storage.Client(project=settings.GCS_PROJECT_ID)

    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob_name = os.path.basename(filepath)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(filepath)
    logger.info("[gcs] uploaded %s -> gs://%s/%s", filepath, settings.GCS_BUCKET_NAME, blob_name)
    return blob_name


def _upload_to_b2(filepath: str) -> str:
    """Upload *filepath* to the configured B2 bucket and return the file ID."""
    from b2sdk.v2 import InMemoryAccountInfo, B2Api  # imported lazily

    if not settings.B2_ACCOUNT_ID or not settings.B2_APPLICATION_KEY:
        raise RuntimeError("B2_ACCOUNT_ID and B2_APPLICATION_KEY are required for B2 uploads")
    if not settings.B2_BUCKET_NAME:
        raise RuntimeError("B2_BUCKET_NAME is not set")

    account_info = InMemoryAccountInfo()
    b2_api = B2Api(account_info)
    b2_api.authorize_account("production", settings.B2_ACCOUNT_ID, settings.B2_APPLICATION_KEY)
    bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)
    file_info = bucket.upload_local_file(local_file=filepath)
    logger.info(
        "[b2] uploaded %s -> b2://%s/%s (file_id=%s)",
        filepath,
        settings.B2_BUCKET_NAME,
        file_info.file_name,
        file_info.id_,
    )
    return file_info.id_


def upload(filepath: str, providers: list[str] | None = None) -> dict:
    """Upload *filepath* to one or both cloud backends.

    Parameters
    ----------
    filepath:
        Path to the local file to upload (backup dump or file-storage tarball).
    providers:
        Explicit list override, e.g. ``["gcs", "b2"]``.  When ``None`` the
        function checks ``settings.GCS_ENABLED`` / ``settings.B2_ENABLED``.
    """
    if not os.path.isfile(filepath):
        return {"success": False, "error": f"File not found: {filepath}"}

    results = {"file": filepath, "uploads": []}
    if providers is None:
        providers = []
        if settings.GCS_ENABLED:
            providers.append("gcs")
        if settings.B2_ENABLED:
            providers.append("b2")

    if not providers:
        logger.info("No cloud provider enabled; skipping offsite upload for %s", filepath)
        results["skipped"] = True
        return results

    for provider in providers:
        try:
            if provider == "gcs":
                object_name = _upload_to_gcs(filepath)
                results["uploads"].append({"provider": "gcs", "object": object_name, "ok": True})
            elif provider == "b2":
                file_id = _upload_to_b2(filepath)
                results["uploads"].append({"provider": "b2", "file_id": file_id, "ok": True})
            else:
                logger.warning("Unknown cloud provider '%s'; skipping.", provider)
        except Exception as exc:  # noqa: BLE001
            logger.error("Cloud upload to %s failed for %s: %s", provider, filepath, exc)
            results["uploads"].append({"provider": provider, "ok": False, "error": str(exc)})

    results["success"] = all(u["ok"] for u in results["uploads"])
    return results


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: cloud_upload.py <filepath> [--provider gcs|b2]", file=sys.stderr)
        return 2
    filepath = argv[0]
    providers: list[str] | None = None
    if len(argv) > 1 and argv[1] in ("--provider", "-p"):
        providers = [argv[2]]
    result = upload(filepath, providers=providers)
    if result.get("success", False) or result.get("skipped", False):
        return 0
    # Failed upload — non-zero exit so backup.sh / callers know.
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
