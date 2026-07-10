import json
import logging
from config.Config import MwanConfig
from utils import cmd

from pydantic import BaseModel
from pydantic.networks import IPvAnyAddress

logger = logging.getLogger("Route")


class Route(BaseModel):
    dev: str | None
    gateway: IPvAnyAddress | None
    protocol: str | None
    metric: int | None
    prefsrc: IPvAnyAddress | None


def show_route(args: list[str]):
    command = ["ip", "-j", "-4", "route", "show", *args]
    result = cmd(command)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"failed to read route: {command}")
    try:
        routes = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        raise RuntimeError(f"failed to parse route: {result.stdout}")
    return routes


def replace_route(args: list[str]) -> None:
    command = ["ip", "-4", "route", "replace", *args]
    result = cmd(command)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f"failed to replace route: {command}"
        )


def delete_route(args: list[str]):
    command = ["ip", "-4", "route", "delete", *args]
    result = cmd(command)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f"failed to delete route: {command}"
        )


def rrrr(route: Route, metric: int) -> None:
    if metric < 0:
        raise RuntimeError(f"invalid metric {metric}")

    base_command = ["ip", "-4", "route", "replace", "default"]
    if route.metric == metric:
        logger.info(f"skip to replace route: dev={route.dev} metric={metric}")
        return
    if route.gateway:
        base_command.extend(["via", route.gateway])
    if route.dev:
        base_command.extend(["dev", route.dev, "metric", str(metric)])
    if route.protocol:
        base_command.extend(["proto", route.protocol])
    if route.prefsrc:
        base_command.extend(["src", route.prefsrc])

    replace_route(base_command)


def get_dev_default_route(dev: str) -> Route:
    defaults = show_route(["default", "dev", dev])
    if not defaults:
        raise RuntimeError(f"no default route found for dev {dev}")

    default = min(defaults, key=lambda item: int(item.get("metric", 0)))
    return Route(
        dev=dev,
        gateway=default.get("gateway"),
        protocol=default.get("protocol"),
        metric=default.get("metric") or 0,
        prefsrc=default.get("prefsrc"),
    )


def apply_route(config: MwanConfig, state: str) -> None:
    primary_route = get_dev_default_route(config.primary.dev)
    backup_route = get_dev_default_route(config.backup.dev)
    if state == "DOWN":
        metric = config.backup.metric + config.primary.step
    elif state == "UP":
        metric = max(config.backup.metric - config.primary.step, 0)
    else:
        raise RuntimeError(f"invalid route state {state}")

    if backup_route.metric != config.backup.metric:
        rrrr(backup_route, config.backup.metric)
    rrrr(primary_route, metric)
    logger.warning(
        f"{config.primary.dev} is {state} switch to {config.backup.dev} with metric {metric}"
    )
