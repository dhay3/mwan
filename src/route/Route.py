import json
import logging
from utils import cmd

from typing import Any
from pydantic import BaseModel

logger = logging.getLogger('Route')


class Route(BaseModel):
    dev: str | None
    gateway: str | None
    protocol: str | None
    metric: int | None
    prefsrc: str | None


def show_route(args: list[Any]):
    command = ['ip', '-j', '-4', 'route', 'show', *args]
    result = cmd(command)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f'failed to read route: {command}')
    try:
        routes = json.loads(result.stdout or '[]')
    except json.JSONDecodeError:
        raise RuntimeError(f'failed to parse route: {result.stdout}')
    logger.debug(f'route read: {command}')
    return routes


def add_route(args: list[Any]):
    command = ['ip', '-4', 'route', 'add', *args]
    result = cmd(command)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f'failed to add route: {command}')
    logger.debug(f'route added: {command}')
    return True


def delete_route(args: list[Any]):
    command = ['ip', '-4', 'route', 'delete', *args]
    result = cmd(command)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f'failed to delete route: {command}'
        )
    logger.debug(f'route deleted: {command}')
    return True


def replace_route(args: list[Any]):
    command = ['ip', '-4', 'route', 'replace', *args]
    result = cmd(command)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f'failed to replace route: {command}'
        )
    logger.debug(f'route replaced: {command}')
    return True
