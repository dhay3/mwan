import logging


LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'

logging.basicConfig(
    format=LOG_FORMAT,
    level=logging.INFO,
)


def set_debug(debug: int):
    level = logging.DEBUG if debug else logging.INFO
    logging.getLogger().setLevel(level)
    for handler in logging.getLogger().handlers:
        handler.setLevel(level)
