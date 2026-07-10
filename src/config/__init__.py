import tomllib
import logging


from pathlib import Path
from .Config import MwanConfig


logger = logging.getLogger("Config")


def load_config(path: Path) -> MwanConfig:
    with path.open("rb") as config_file:
        logger.info(f"loading config from {path}")
        data = tomllib.load(config_file)
    return MwanConfig.model_validate(data)


__all__ = [
    MwanConfig,
    load_config,
]
