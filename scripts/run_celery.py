"""
Celery Task Runner Entrypoint
"""
import sys

from app.tasks.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start(argv=sys.argv[1:] if len(sys.argv) > 1 else ["worker", "--loglevel=INFO"])