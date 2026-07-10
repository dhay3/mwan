import logging

from .Route import (
    Route,
    show_route,
    replace_route,
)
from config import MwanConfig
from config.State import STATE

logger = logging.getLogger("Route")


def get_default_route(dev: str) -> Route:
    defaults = show_route(["default", "dev", dev])
    if not defaults:
        raise RuntimeError(f"no default route for dev: {dev}")

    default = min(defaults, key=lambda item: int(item.get("metric", 0)))
    return Route(
        dev=dev,
        gateway=default.get("gateway"),
        protocol=default.get("protocol"),
        metric=default.get("metric"),
        prefsrc=default.get("prefsrc"),
    )


def replace_default_route(route: Route, metric: int):
    if metric < 0:
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


def apply_default_route(config: MwanConfig, state: STATE):
    primary_deft = get_default_route(config.primary.dev)
    backup_deft = get_default_route(config.backup.dev)
    if state == STATE.Backup:
        metric = backup_deft.metric + config.primary.step
    elif state == STATE.Primary:
        metric = max(backup_deft.metric - config.primary.step, 0)

    replace_default_route(primary_deft, metric)
    logger.warning(f"{config.primary.dev} switched to {state.name}")


__all__ = [apply_default_route]
