import json
import logging
from typing import Any
from pydantic import BaseModel
from utils import cmd
from error import MwanRouteError

logger = logging.getLogger('Route')


class Route(BaseModel):
    dst: str | None = None
    gateway: str | None = None
    dev: str | None = None
    protocol: str | None = None
    prefsrc: str | None = None
    metric: int | None = None


def show_route(args: list[Any]) -> list[Route]:
    command = ['ip', '-j', '-4', 'route', 'show', *args]
    result = cmd(command)
    if result.returncode != 0:
        raise MwanRouteError(
            f'failed to read route: {command} trace: {result.stderr.strip()}'
        )
    try:
        routes = json.loads(result.stdout or '[]')
    except json.JSONDecodeError as exec:
        raise MwanRouteError(f'failed to parse route: {command}') from exec
    logger.debug(f'show: {command}')
    return [Route.model_validate(route) for route in routes]


def get_route(dst: str, args: list[Any]) -> Route:
    command = ['ip', '-j', '-4', 'route', 'get', dst, *args]
    result = cmd(command)
    if result.returncode != 0:
        raise MwanRouteError(
            f'failed to get route: {command} trace: {result.stderr.strip()}'
        )
    try:
        routes = json.loads(result.stdout or '[]')
    except json.JSONDecodeError as e:
        raise MwanRouteError(f'failed to parse route: {command}') from e
    if not routes:
        raise MwanRouteError(f'failed to get route: {dst}')
    # logger.debug(f'get: {command}')
    return Route.model_validate(routes[0])


def add_route(args: list[Any]):
    command = ['ip', '-4', 'route', 'add', *args]
    result = cmd(command)
    if result.returncode != 0:
        raise MwanRouteError(
            f'failed to add route: {command} trace: {result.stderr.strip()}'
        )
    logger.debug(f'add: {command}')
    return True


def delete_route(args: list[Any]):
    command = ['ip', '-4', 'route', 'delete', *args]
    result = cmd(command)
    if result.returncode != 0:
        raise MwanRouteError(
            f'failed to delete route: {command} trace: {result.stderr.strip()}'
        )
    logger.debug(f'delete: {command}')
    return True


def replace_route(args: list[Any]):
    command = ['ip', '-4', 'route', 'replace', *args]
    result = cmd(command)
    if result.returncode != 0:
        raise MwanRouteError(
            f'failed to replace route: {command} trace: {result.stderr.strip()}'
        )
    logger.debug(f'replace: {command}')
    return True


def get_gateway(dst: str, args: list[Any]) -> str:
    route = get_route(dst, args)
    if route.gateway:
        return route.gateway
    raise MwanRouteError(f'fail to get gateway: {dst}')
