import logging
from pathlib import Path
from threading import Event


from config import MwanConfig, load_config, get_config_mtime
from config.State import STATE
from logger import set_debug
from probe import probe
from route import switch_defualt_route


logger = logging.getLogger('Monitor')


class Monitor:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config: MwanConfig = load_config(config_path)
        self.config_mtime = get_config_mtime(config_path)
        set_debug(self.config.debug)
        self.down_cnt = 0
        self.up_cnt = 0
        self.state: STATE = STATE.Primary
        self.quit: Event = Event()

    def stop(self, signum: int, frame=None):
        self.quit.set()

    def run(self):
        while not self.quit.is_set():
            self.reload_config()
            self.delegate()

            if self.quit.wait(self.config.probe.delay):
                break

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
        enable_log = self.state == STATE.Primary
        down = probe(self.config, enable_log)

        if down:
            self.down_cnt += 1
            self.up_cnt = 0
            oughta_down = (
                self.config.probe.fast_down or self.down_cnt >= self.config.probe.down
            )
            if enable_log:
                logger.debug(
                    'down_cnt=%s down_threshold=%s',
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
            if not enable_log:
                logger.debug(
                    'up_cnt=%s up_threshold=%s',
                    self.up_cnt,
                    self.config.probe.up,
                )
            if oughta_up and self.state != STATE.Primary:
                switch_defualt_route(self.config, STATE.Primary)
                self.state = STATE.Primary
