import logging

from .Route import (
    Route,
    show_route,
    replace_route,
)
from config import MwanConfig

logger = logging.getLogger("Route")


def get_default_route(dev: str) -> Route:
    defaults = show_route(["default", "dev", dev])
    if not defaults:
        raise RuntimeError(f"no default route for dev: {dev}")

    default = min(defaults, key=lambda item: int(item.get("metric", "0")))
    return Route(
        dev=dev,
        gateway=default.get("gateway"),
        protocol=default.get("protocol"),
        metric=default.get("metric"),
        prefsrc=default.get("prefsrc"),
    )


def replace_default_route(route: Route, metric: str):
    if int(metric) < 0:
        raise RuntimeError(f"negative metric: {metric}, route: {route}")
    if route.metric == metric:
        logger.info(f"same metric: {metric}, route={route}")
        return

    args = ["default"]

    if route.gateway:
        args.extend(["via", route.gateway])
    if route.dev:
        args.extend(["dev", route.dev, "metric", str(metric)])
    if route.protocol:
        args.extend(["proto", route.protocol])
    if route.prefsrc:
        args.extend(["src", route.prefsrc])

    args.extend(["metric", metric])

    replace_route(args)


def apply_default_route(config: MwanConfig, state: str):
    primary_deft = get_default_route(config.primary.dev)
    backup_deft = get_default_route(config.backup.dev)
    if state == "DOWN":
        metric = backup_deft.metric + config.primary.step
    elif state == "UP":
        metric = max(backup_deft.metric - config.primary.step, 0)
    else:
        raise RuntimeError(f"invalid route state {state}")

    if backup_deft.metric != config.backup.metric:
        replace_default_route(backup_deft, config.backup.metric)
    replace_default_route(primary_deft, metric)
    logger.warning(
        f"{config.primary.dev} is {state} switch to {config.backup.dev} with metric {metric}"
    )
