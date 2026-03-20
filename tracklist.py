#!/usr/bin/env python3
import logging
import logging.config
import re

import psycopg2

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "/var/log/ferakh.log",
            "level": "INFO",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": "manti",
    "user": "manti",
    "password": "manti",
}


def get_filename_from_release(release: str) -> str:
    filename = release.replace("release/", "")
    filename = re.sub(r"\.mp3$", ".txt", filename, flags=re.IGNORECASE)
    filename = re.sub(r"\.flac$", ".txt", filename, flags=re.IGNORECASE)
    return filename


def fetch_tracklists() -> list[tuple[str, str]]:
    conn = psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT release, tracklist FROM blog_post WHERE tracklist IS NOT NULL AND tracklist != ''"
    )
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


def save_tracklist(release: str, tracklist: str) -> None:
    filename = get_filename_from_release(release)
    with open(f"tracklists/{filename}", "w") as f:
        f.write(tracklist)
    logger.info(f"Saved: {filename}")


def main() -> None:
    logger.info("Starting tracklist export")
    results = fetch_tracklists()
    for release, tracklist in results:
        save_tracklist(release, tracklist)
    logger.info(f"Exported {len(results)} tracklists")


if __name__ == "__main__":
    main()
