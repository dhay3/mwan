import tomllib
import logging


from pathlib import Path
from .Config import MwanConfig
from .State import STATE
from error import MwanConfigError

logger = logging.getLogger('Config')


def load_config(path: Path) -> MwanConfig:
    try:
        with path.open('rb') as config_file:
            logger.info(f'loading config from {path}')
            data = MwanConfig.model_validate(tomllib.load(config_file))

    except Exception as exec:
        raise MwanConfigError(f'loading config from {path} failed') from exec
    return data


def get_config_mtime(path: Path):
    try:
        return path.stat().st_mtime
    except Exception:
        raise MwanConfigError(f'reading config stat from {path} failed')


def get_state(config: MwanConfig) -> STATE:
    from route import show_default_routes

    def route_metric(route):
        return route.metric if route.metric is not None else 0

    primary_routes = show_default_routes(config.primary.dev)
    backup_routes = show_default_routes(config.backup.dev)

    if not primary_routes or not backup_routes:
        return STATE.UNKNOWN

    primary_metric = route_metric(min(primary_routes, key=route_metric))
    backup_metric = route_metric(min(backup_routes, key=route_metric))

    if primary_metric < backup_metric:
        return STATE.PRIMARY
    if primary_metric > backup_metric:
        return STATE.BACKUP
    return STATE.UNKNOWN


__all__ = [
    MwanConfig,
    load_config,
    get_config_mtime,
    get_state,
]
