import logging
from threading import Event

from config import MwanConfig
from config.State import STATE
from probe import probe
from route import apply_default_route


logger = logging.getLogger("Monitor")


class Monitor:
    def __init__(self, config: MwanConfig):
        self.config = config
        self.quit = Event()
        self.down_cnt = 0
        self.up_cnt = 0
        self.state: STATE

    def stop(self, signum: int):
        logger.info(f"mwan stopping {signum}")
        self.quit.set()

    def run(self):
        logger.info(
            f"mwan started: primary={self.config.primary.dev} backup={self.config.backup.dev} hosts={','.join(self.config.probe.address)}"
        )

        while not self.quit.is_set():
            self.delegate()

            if self.quit.wait(self.config.probe.delay):
                break

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
            if oughta_down and self.state != "Backup":
                apply_default_route(self.config, "Backup")
                self.state = "Backup"
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
            if oughta_up and self.state != "Primary":
                apply_default_route(self.config, "Primary")
                self.state = "Primary"
