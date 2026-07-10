import logging


LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

logging.basicConfig(
    format=LOG_FORMAT,
    level=logging.INFO,
)
