import tomllib
import logging


from pathlib import Path
from .Config import MwanConfig
from error import MwanConfigError

logger = logging.getLogger('Config')


def load_config(path: Path) -> MwanConfig:
    try:
        with path.open('rb') as config_file:
            logger.info(f'loading config from {path}')
            data = tomllib.load(config_file)
    except Exception as exc:
        raise MwanConfigError(f'failed to load config from {path}') from exc
    return MwanConfig.model_validate(data)


def get_config_mtime(path: Path):
    try:
        return path.stat().st_mtime
    except Exception as exc:
        raise MwanConfigError(f'failed to get config mtime from {path}') from exc


__all__ = [
    MwanConfig,
    load_config,
    get_config_mtime,
]
