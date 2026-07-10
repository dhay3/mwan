import json
from utils import cmd

from pydantic import BaseModel


class Route(BaseModel):
    dev: str | None
    gateway: str | None
    protocol: str | None
    metric: int | None
    prefsrc: str | None


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


def add_route(args: list[str]):
    pass


def delete_route(args: list[str]):
    command = ["ip", "-4", "route", "delete", *args]
    result = cmd(command)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f"failed to delete route: {command}"
        )


def replace_route(args: list[str]):
    command = ["ip", "-4", "route", "replace", *args]
    result = cmd(command)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f"failed to replace route: {command}"
        )
