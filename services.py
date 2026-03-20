import logging
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from psd_tools import PSDImage

from settings import (
    BASE_PATH,
    BG_CROP_SIZE,
    FONT_SIZE,
    LINE_HEIGHT,
    SUPPORTED_IMAGE_EXTENSIONS,
    TARGET_SIZE_BG,
    TARGET_SIZE_THUMB,
    TEXT_COORDS,
    THUMB_COORDS,
)

BRIGHTNESS_THRESHOLD = 200

logger = logging.getLogger(__name__)


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


def get_average_brightness(img: Image.Image) -> float:
    gray = img.convert("L")
    pixels = list(gray.getdata())
    return sum(pixels) / len(pixels)


def create_blurred_background(
    original_path: str,
) -> tuple[Image.Image, Image.Image | None]:
    img = Image.open(f"{BASE_PATH}/{original_path}").convert("RGB")
    img = resize_to_shortest_dim(img, TARGET_SIZE_BG)
    img = img.filter(ImageFilter.GaussianBlur(radius=100))

    crop_w, crop_h = BG_CROP_SIZE
    left = (img.width - crop_w) // 2
    top = (img.height - crop_h) // 2
    img = img.crop((left, top, left + crop_w, top + crop_h))

    brightness = get_average_brightness(img)
    overlay = None
    if brightness > BRIGHTNESS_THRESHOLD:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 100))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(0.8)

    return img, overlay


def create_thumbnail(original_path: str) -> Image.Image:
    img = Image.open(f"{BASE_PATH}/{original_path}").convert("RGBA")
    img = resize_to_shortest_dim(img, TARGET_SIZE_THUMB)
    return img


def create_text_image(text: str) -> Image.Image:
    font = ImageFont.truetype("fonts/MyriadPro-Regular.otf", FONT_SIZE)
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

    lines = text.split("\n")
    line_heights = []
    max_width = 0
    for line in lines:
        bbox = dummy.textbbox((0, 0), line, font=font)
        line_height = (bbox[3] - bbox[1]) * LINE_HEIGHT
        line_heights.append(math.floor(line_height))
        width = bbox[2] - bbox[0]
        if width > max_width:
            max_width = width

    total_height = sum(line_heights) + 10

    image = Image.new("RGBA", (max_width + 10, int(total_height)), (0, 0, 0, 0))  # ty: ignore[invalid-argument-type]
    draw = ImageDraw.Draw(image)

    y = 5
    for line, line_height in zip(lines, line_heights):
        draw.text((5, y), line, fill=(255, 255, 255, 255), font=font)
        y += line_height

    return image


def create_psd_from_images(
    background: Image.Image,
    thumbnail: Image.Image,
    text_img: Image.Image | None,
    overlay: Image.Image | None,
) -> PSDImage:
    psd = PSDImage.new(
        "RGBA", (int(background.width), int(background.height)), color=(0, 0, 0, 0)
    )

    psd.create_pixel_layer(background, name="Background", left=0, top=0)

    if overlay:
        psd.create_pixel_layer(overlay, name="Overlay", left=0, top=0)

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

    background, overlay = create_blurred_background(image_path)
    thumbnail = create_thumbnail(image_path)

    text_img = None
    text_file = get_text_filename(image_path)
    if text_file:
        with open(text_file, "r") as f:
            text = f.read().strip()
        if text:
            text_img = create_text_image(text)
            logger.info(f"  Added text from: {text_file}")

    psd = create_psd_from_images(background, thumbnail, text_img, overlay)

    output_path = f"{BASE_PATH}/covers/{image_path.replace('jpg', 'psd')}"
    psd.save(output_path)
    logger.info(f"  Saved: {output_path}")

    jpeg_path = output_path.replace(".psd", ".jpg")
    result_img = psd.composite()
    result_img = result_img.convert("RGB")
    result_img.save(jpeg_path, "JPEG")
    logger.info(f"  Saved: {jpeg_path}")
