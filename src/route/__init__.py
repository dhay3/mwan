import logging

from copy import deepcopy

from .Route import (
    Route,
    show_route,
    add_route,
    delete_route,
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


def add_default_route(route: Route):
    args = ["default"]

    if route.gateway:
        args.extend(["via", route.gateway])
    if route.dev:
        args.extend(["dev", route.dev])
    if route.protocol:
        args.extend(["proto", route.protocol])
    if route.prefsrc:
        args.extend(["src", route.prefsrc])
    if route.metric is not None:
        args.extend(["metric", str(route.metric)])

    return add_route(args)


def del_default_route(route: Route):
    args = ["default"]

    if route.gateway:
        args.extend(["via", route.gateway])
    if route.dev:
        args.extend(["dev", route.dev])
    if route.protocol:
        args.extend(["proto", route.protocol])
    if route.prefsrc:
        args.extend(["src", route.prefsrc])
    if route.metric is not None:
        args.extend(["metric", str(route.metric)])

    return delete_route(
        ["default", "via", route.gateway, "dev", route.dev, "metric", str(route.metric)]
    )


def switch_defualt_route(config: MwanConfig, state: STATE):
    primary_deft = get_default_route(config.primary.dev)
    primary_deft_copy = deepcopy(primary_deft)
    backup_deft = get_default_route(config.backup.dev)
    backup_metric = backup_deft.metric or 0
    if state == STATE.Backup:
        primary_deft.metric = backup_metric + config.primary.step
    elif state == STATE.Primary:
        primary_deft.metric = max(backup_metric - config.primary.step, 0)

    if add_default_route(primary_deft) and del_default_route(primary_deft_copy):
        logger.warning(f"{config.primary.dev} switched to {state.name}")


__all__ = [switch_defualt_route]
