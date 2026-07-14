#!/usr/bin/env python3

import argparse
import logging
import os

import signal
from pathlib import Path

import logger as LOG  # noqa: F401

logger = logging.getLogger("Main")


def build_parse():
    parser = argparse.ArgumentParser(
        prog="mwan",
        usage="%(prog)s [options]",
        epilog="released under MIT license",
        description="IP SLA implementation for Linux.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default="/opt/mwan/mwan_config.toml",
        help="path to config file (default: %(default)s)",
    )
    return parser


def main() -> int:
    args = build_parse().parse_args(["-c", "mwan_config.toml"])

    try:
        from monitor.Monitor import Monitor

        monitor = Monitor(args.config)

        def interrupt(signum: int, frame=None):
            monitor.stop(signum, frame)
            logging.shutdown()
            os._exit(0)

        signal.signal(signal.SIGINT, interrupt)
        signal.signal(signal.SIGTERM, monitor.stop)
        monitor.run()
    except Exception:
        logger.exception("stopped with an error")
        return 1
    return 0
