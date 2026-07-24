#!/usr/bin/env python3

import argparse
import logging
import signal
from pathlib import Path


def build_parse():
    parser = argparse.ArgumentParser(
        prog='mwan',
        usage='%(prog)s [options]',
        epilog='released under MIT license',
        description='IP SLA implementation for Linux.',
    )
    parser.add_argument(
        '-c',
        '--config',
        type=Path,
        default='/opt/mwan/mwan.toml',
        help='path to config file (default: %(default)s)',
    )
    return parser


def main() -> int:
    args = build_parse().parse_args()

    try:
        import utils.logger as LOG  # noqa: F401
        from utils.lock import Lock
        from monitor.Monitor import Monitor

        locker = Lock(Path('/run/lock/mwan.lock'))
        logger = logging.getLogger('Main')

        with locker:
            monitor = Monitor(args.config)

            signal.signal(signal.SIGINT, monitor.stop)
            signal.signal(signal.SIGTERM, monitor.stop)
            monitor.run()
    except Exception:
        logger.exception('stopped with an error')
        return 1
    return 0
