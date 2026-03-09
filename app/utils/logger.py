import logging
import os


def get_logger(name: str):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(os.getenv("RESBOT_LOG_LEVEL", "INFO"))

    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler("logs/resiliencebot.log")
    console_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger