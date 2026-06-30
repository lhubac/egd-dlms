import logging

from egd_dlms.config import LOGGING


def setup_logger() -> logging.Logger:
    level_name = LOGGING.get("level", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    return logging.getLogger("egd-dlms")
