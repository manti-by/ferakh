#!/usr/bin/env python3
import argparse
import logging
import logging.config
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from psd_tools import PSDImage

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "/var/log/ferakh.log",
            "level": "WARNING",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

BASE_PATH = "/home/manti/download/Youtube"
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
TARGET_SIZE_BG = 1920
TARGET_SIZE_THUMB = 500
THUMB_COORDS = (300, 200)
TEXT_COORDS = (700, 200)


def is_image(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_IMAGE_EXTENSIONS


def get_text_filename(image_path: str) -> str | None:
    base = os.path.splitext(f"{BASE_PATH}/{image_path}")[0]
    for ext in ["", ".txt"]:
        text_path = base + ext
        if os.path.exists(text_path):
            return text_path
    return None


def resize_to_shortest_dim(img: Image.Image, target: int) -> Image.Image:
    width, height = img.size
    if width < height:
        new_width = target
        new_height = int(height * target / width)
    else:
        new_height = target
        new_width = int(width * target / height)
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def create_blurred_background(original_path: str) -> Image.Image:
    img = Image.open(f"{BASE_PATH}/{original_path}").convert("RGB")
    img = resize_to_shortest_dim(img, TARGET_SIZE_BG)
    img = img.filter(ImageFilter.GaussianBlur(radius=15))
    return img


def create_thumbnail(original_path: str) -> Image.Image:
    img = Image.open(f"{BASE_PATH}/{original_path}").convert("RGBA")
    img = resize_to_shortest_dim(img, TARGET_SIZE_THUMB)
    return img


def create_text_image(text: str) -> Image.Image:
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/roboto/unhint/Roboto-Regular.ttf", 13
        )
    except (OSError, IOError):
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf", 13
            )
        except (OSError, IOError):
            font = ImageFont.load_default()

    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = dummy.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    img = Image.new("RGBA", (width + 10, height + 10), (0, 0, 0, 0))  # ty: ignore[invalid-argument]
    draw = ImageDraw.Draw(img)
    draw.text((5, 5), text, fill=(255, 255, 255, 255), font=font)
    return img


def create_psd_from_images(
    background: Image.Image, thumbnail: Image.Image, text_img: Image.Image | None
) -> PSDImage:
    psd = PSDImage.new(
        "RGBA", (int(background.width), int(background.height)), color=(0, 0, 0, 0)
    )

    psd.create_pixel_layer(background, name="Background", left=0, top=0)

    psd.create_pixel_layer(
        thumbnail, name="Thumbnail", left=THUMB_COORDS[0], top=THUMB_COORDS[1]
    )

    if text_img:
        psd.create_pixel_layer(
            text_img, name="Text", left=TEXT_COORDS[0], top=TEXT_COORDS[1]
        )

    return psd


def process_image(image_path: str, dry_run: bool = False) -> None:
    if dry_run:
        logger.info(f"Would process: {image_path}")
        text_file = get_text_filename(image_path)
        if text_file:
            logger.info(f"  Would add text from: {text_file}")
        else:
            logger.info("  No text file found")
        return

    logger.info(f"Processing: {image_path}")

    background = create_blurred_background(image_path)
    thumbnail = create_thumbnail(image_path)

    text_img = None
    text_file = get_text_filename(image_path)
    if text_file:
        with open(text_file, "r") as f:
            text = f.read().strip()
        if text:
            text_img = create_text_image(text)
            logger.info(f"  Added text from: {text_file}")

    psd = create_psd_from_images(background, thumbnail, text_img)

    output_path = f"covers/{image_path.replace('jpg', 'psd')}"
    psd.save(output_path)
    logger.info(f"  Saved: {output_path}")


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
