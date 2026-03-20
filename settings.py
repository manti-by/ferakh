BASE_PATH = "/home/manti/download/Youtube"

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg"}

TARGET_SIZE_BG = 1920
BG_CROP_SIZE = (1920, 1080)

TARGET_SIZE_THUMB = 600
THUMB_COORDS = (250, 250)

TEXT_COORDS = (1100, 300)
FONT_SIZE = 32
LINE_HEIGHT = 1.3

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
