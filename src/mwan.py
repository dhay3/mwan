#!/usr/bin/env python3

from __future__ import annotations

import argparse

import signal
from pathlib import Path

from config import load_config

import logging
from monitor.Monitor import Monitor


logger = logging.getLogger("main")


def define_options():
    parser = argparse.ArgumentParser(
        prog="mwan",
        usage="%(prog)s [options]",
        epilog="released under MIT license",
        description="IP SLA implementation for Linux.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default="/opt/mwan/mwan_config.toml",
        help="path to config file (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> int:
    args = define_options()

    try:
        monitor = Monitor(load_config(args.config))
        signal.signal(signal.SIGINT, monitor.stop)
        signal.signal(signal.SIGTERM, monitor.stop)
        monitor.run()
    except Exception:
        # logger.exception('mwan stopped with an error')
        return 1
    return 0


main()
