import logging
from pathlib import Path
from threading import Event

from config import MwanConfig, load_config
from config.State import STATE
from probe import probe
from route import switch_defualt_route


logger = logging.getLogger("Monitor")


class Monitor:
    def __init__(self, config: MwanConfig, config_path: Path | None = None):
        self.config = config
        self.config_path = config_path
        self.config_mtime_ns = self.get_config_mtime_ns()
        self.quit = Event()
        self.down_cnt = 0
        self.up_cnt = 0
        self.state: STATE = STATE.Primary

    def stop(self, signum: int, frame=None):
        logger.info(f"mwan stopping {signum}")
        self.quit.set()

    def run(self):
        logger.info(
            f"mwan started: primary={self.config.primary.dev} backup={self.config.backup.dev}"
        )

        while not self.quit.is_set():
            self.reload_config_if_changed()
            self.delegate()

            if self.quit.wait(self.config.probe.delay):
                break

    def get_config_mtime_ns(self) -> int | None:
        if self.config_path is None:
            return None
        try:
            return self.config_path.stat().st_mtime_ns
        except OSError:
            logger.warning("config file is not readable: %s", self.config_path)
            return None

    def reload_config_if_changed(self):
        mtime_ns = self.get_config_mtime_ns()
        if mtime_ns is None or mtime_ns == self.config_mtime_ns:
            return

        self.config_mtime_ns = mtime_ns
        try:
            config = load_config(self.config_path)
        except Exception:
            logger.exception("failed to reload config: %s", self.config_path)
            return

        self.config = config
        self.down_cnt = 0
        self.up_cnt = 0
        logger.info(
            "config reloaded: primary=%s backup=%s",
            self.config.primary.dev,
            self.config.backup.dev,
        )

    def delegate(self):
        down = probe(self.config)

        if down:
            self.down_cnt += 1
            self.up_cnt = 0
            oughta_down = (
                self.config.probe.fast_down or self.down_cnt >= self.config.probe.down
            )
            logger.info(
                "down_cnt=%s down_threshold=%s",
                self.down_cnt,
                self.config.probe.down,
            )
            if oughta_down and self.state != STATE.Backup:
                switch_defualt_route(self.config, STATE.Backup)
                self.state = STATE.Backup
            return
        else:
            self.up_cnt += 1
            self.down_cnt = 0
            oughta_up = self.config.probe.fast_up or self.up_cnt >= self.config.probe.up
            logger.info(
                "up_cnt=%s up_threshold=%s",
                self.up_cnt,
                self.config.probe.up,
            )
            if oughta_up and self.state != STATE.Primary:
                switch_defualt_route(self.config, STATE.Primary)
                self.state = STATE.Primary
