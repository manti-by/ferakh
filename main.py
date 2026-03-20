#!/usr/bin/env python3
import argparse
import logging.config
import os

from services import is_image, process_image
from settings import LOGGING_CONFIG, BASE_PATH

logging.config.dictConfig(LOGGING_CONFIG)


def main():
    parser = argparse.ArgumentParser(
        description="Process images with blur background and thumbnail"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Log actions without creating files"
    )
    args = parser.parse_args()

    for filename in os.listdir(BASE_PATH):
        if is_image(filename):
            process_image(filename, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
