#!/usr/bin/env python3

import argparse

import signal
from pathlib import Path

import logging


logger = logging.getLogger("main")


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
    args = build_parse().parse_args()

    try:
        # from config import load_config
        from monitor.Monitor import Monitor

        monitor = Monitor(args.config)

        def interrupt(signum: int, frame=None):
            monitor.stop(signum, frame)
            raise KeyboardInterrupt

        signal.signal(signal.SIGINT, interrupt)
        signal.signal(signal.SIGTERM, monitor.stop)
        monitor.run()
    except KeyboardInterrupt:
        logger.info("mwan stopped by keyboard interrupt")
        return 0
    except Exception:
        logger.exception("mwan stopped with an error")
        return 1
    return 0
