import json
import logging
from copy import deepcopy
from pathlib import Path


from .Route import (
    Route,
    show_route,
    add_route,
    delete_route,
)
from config import MwanConfig
from config.State import STATE

logger = logging.getLogger('Route')


def show_default_route(dev: str) -> Route:
    defaults = show_default_routes(dev)
    if not defaults:
        raise RuntimeError(f'no default route for dev: {dev}')

    return min(defaults, key=lambda item: item.metric or 0)


def show_default_routes(dev: str) -> list[Route]:
    return [
        route.model_copy(update={'dev': route.dev or dev})
        for route in show_route(['default', 'dev', dev])
    ]


def add_default_route(route: Route):
    args = ['default']

    if route.gateway:
        args.extend(['via', route.gateway])
    if route.dev:
        args.extend(['dev', route.dev])
    if route.protocol:
        args.extend(['protocol', route.protocol])
    if route.prefsrc:
        args.extend(['src', route.prefsrc])
    if route.metric is not None:
        args.extend(['metric', str(route.metric)])

    return add_route(args)


def del_default_route(route: Route):
    args = ['default']

    if route.gateway:
        args.extend(['via', route.gateway])
    if route.dev:
        args.extend(['dev', route.dev])
    if route.protocol:
        args.extend(['protocol', route.protocol])
    if route.prefsrc:
        args.extend(['src', route.prefsrc])
    if route.metric is not None:
        args.extend(['metric', str(route.metric)])

    return delete_route(args)


def same_route_bypass_metric(left: Route, right: Route) -> bool:
    return left.model_copy(update={'metric': None}) == right.model_copy(
        update={'metric': None}
    )


def switch_defualt_route(config: MwanConfig, state: STATE):
    primary_deft = show_default_route(config.primary.dev)
    primary_deft_copy = deepcopy(primary_deft)
    backup_deft = show_default_route(config.backup.dev)
    backup_metric = backup_deft.metric or 0
    if state == STATE.BACKUP:
        primary_deft.metric = backup_metric + config.primary.step
    elif state == STATE.PRIMARY:
        primary_deft.metric = max(backup_metric - config.primary.step, 0)

    if primary_deft.metric == primary_deft_copy.metric:
        return

    if add_default_route(primary_deft) and del_default_route(primary_deft_copy):
        logger.warning(f'switched to: {state.name}')


def save_routes(config: MwanConfig, path: Path):
    devices = dict.fromkeys([config.primary.dev, config.backup.dev])
    routes = []
    for dev in devices:
        device_routes = show_default_routes(dev)
        routes.extend(device_routes)
    state = {
        'routes': [route.model_dump(mode='json') for route in routes],
    }
    temp = path.with_suffix(f'{path.suffix}.tmp')
    temp.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )
    temp.replace(path)
    logger.info(f'saved routes state: {path}')


def restore_routes(path: Path):
    if not path.exists():
        return

    state = json.loads(path.read_text(encoding='utf-8'))
    stored_routes = [Route.model_validate(route) for route in state.get('routes', [])]

    routes: dict[str, list[Route]] = {}
    for desired_route in stored_routes:
        routes.setdefault(desired_route.dev, []).append(desired_route)

    for dev, desired_routes in routes.items():
        current_routes = show_default_routes(dev)
        for desired_route in desired_routes:
            if desired_route not in current_routes:
                add_default_route(desired_route)

        for current_route in current_routes:
            is_variant = any(
                same_route_bypass_metric(current_route, desired_route)
                for desired_route in desired_routes
            )
            if current_route not in desired_routes and is_variant:
                del_default_route(current_route)

    path.unlink()
    logger.info(f'restored routes state: {path}')


__all__ = [
    restore_routes,
    save_routes,
    switch_defualt_route,
]
