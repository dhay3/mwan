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
from error import MwanRouteError

logger = logging.getLogger('Route')


def show_default_routes(dev: str) -> list[Route]:
    return [
        route.model_copy(update={'dev': route.dev or dev})
        for route in show_route(['default', 'dev', dev])
    ]


def show_default_route(dev: str) -> Route:
    defaults = show_default_routes(dev)
    if not defaults:
        raise MwanRouteError(f'no default route for dev: {dev}')
    if len(defaults) > 1:
        raise MwanRouteError(f'multiple default routes for dev: {dev}')

    return defaults[0]


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


def set_default_route_metric(route: Route, metric: int) -> bool:
    if (route.metric or 0) == metric:
        return False

    previous_route = deepcopy(route)
    route.metric = metric
    if add_default_route(route) and del_default_route(previous_route):
        return True
    return False


def switch_default_route(config: MwanConfig, state: STATE):
    primary_deft = show_default_route(config.primary.dev)
    backup_deft = show_default_route(config.backup.dev)
    backup_metric = backup_deft.metric or 0

    if state == STATE.BACKUP:
        return set_default_route_metric(
            primary_deft,
            backup_metric + config.primary.step,
        )

    if state == STATE.PRIMARY:
        primary_metric = max(backup_metric - config.primary.step, 0)
        primary_changed = set_default_route_metric(primary_deft, primary_metric)

        if primary_metric < backup_metric:
            return primary_changed

        backup_changed = set_default_route_metric(
            backup_deft,
            primary_metric + config.primary.step,
        )
        return primary_changed or backup_changed

    return False


def same_route(left: Route, right: Route) -> bool:
    return left.model_copy(update={'metric': None}) == right.model_copy(
        update={'metric': None}
    )


def load_reoutes(path: Path):
    stored_routes = [
        Route.model_validate(route)
        for route in json.loads(path.read_text(encoding='utf-8')).get('routes', [])
    ]
    if not stored_routes:
        raise MwanRouteError(f'stored routes {path} empty')
    return stored_routes


def store_routes(config: MwanConfig, path: Path):
    if path.exists():
        load_reoutes(path)
        logger.warning(f'resume routes from {path}')
        return
    devices = dict.fromkeys([config.primary.dev, config.backup.dev])
    current_routes = []
    for dev in devices:
        device_routes = show_default_routes(dev)
        if not device_routes:
            raise MwanRouteError(f'missing route for {dev}')
        if len(device_routes) > 1:
            raise MwanRouteError(f'multiple default routes for dev: {dev}')
        current_routes.append(device_routes[0])
    stored_routes = {
        'routes': [route.model_dump(mode='json') for route in current_routes],
    }
    temp = path.with_suffix(f'{path.suffix}.tmp')
    temp.write_text(
        json.dumps(stored_routes, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )
    temp.replace(path)
    logger.info(f'store routes to {path}')


def restore_routes(path: Path):
    if not path.exists():
        return

    stored_routes = load_reoutes(path)

    desired_routes: dict[str, list[Route]] = {}
    for stored_route in stored_routes:
        desired_routes.setdefault(stored_route.dev, []).append(stored_route)

    for dev, dev_desired_routes in desired_routes.items():
        current_routes = show_default_routes(dev)
        for stored_route in dev_desired_routes:
            if stored_route not in current_routes:
                add_default_route(stored_route)

        for current_route in current_routes:
            if current_route not in dev_desired_routes and any(
                same_route(current_route, desired_route)
                for desired_route in dev_desired_routes
            ):
                del_default_route(current_route)

    path.unlink()
    logger.info(f'restored routes from {path}')


__all__ = [
    restore_routes,
    store_routes,
    switch_default_route,
]
