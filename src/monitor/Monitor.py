import logging
from pathlib import Path
from threading import Event


from config import MwanConfig, load_config, get_config_mtime
from config.State import STATE
from logger import set_debug
from probe import probe
from route import (
    restore_routes,
    save_routes,
    switch_defualt_route,
)


logger = logging.getLogger('Monitor')


class Monitor:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config: MwanConfig = load_config(config_path)
        self.config_mtime = get_config_mtime(config_path)
        set_debug(self.config.debug)
        self.down_cnt = 0
        self.up_cnt = 0
        self.quit: Event = Event()
        self.state_path = config_path.with_suffix('.db')
        save_routes(self.config, self.state_path)

    def stop(self, signum: int, frame=None):
        self.quit.set()

    def run(self):
        try:
            while not self.quit.is_set():
                self.reload_config()
                self.delegate()

                if self.quit.wait(self.config.probe.delay):
                    break
        finally:
            restore_routes(self.state_path)

    def reload_config(self):
        mtime = get_config_mtime(self.config_path)
        if mtime is None or mtime == self.config_mtime:
            return

        self.config_mtime = mtime
        self.config = load_config(self.config_path)
        set_debug(self.config.debug)
        self.down_cnt = 0
        self.up_cnt = 0

    def delegate(self):
        down = probe(self.config)

        if down:
            self.down_cnt += 1
            self.up_cnt = 0
            oughta_down = (
                self.config.probe.fast_down or self.down_cnt >= self.config.probe.down
            )
            if self.down_cnt <= 3:
                logger.debug(
                    'down_cnt=%s down_threshold=%s',
                    self.down_cnt,
                    self.config.probe.down,
                )
            if oughta_down:
                switch_defualt_route(self.config, STATE.BACKUP)
            return
        else:
            self.up_cnt += 1
            self.down_cnt = 0
            oughta_up = self.config.probe.fast_up or self.up_cnt >= self.config.probe.up
            if self.up_cnt <= 3:
                logger.debug(
                    'up_cnt=%s up_threshold=%s',
                    self.up_cnt,
                    self.config.probe.up,
                )
            if oughta_up:
                switch_defualt_route(self.config, STATE.PRIMARY)
