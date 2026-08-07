import logging
from pathlib import Path
from threading import Event


from config import MwanConfig, load_config, get_config_mtime, get_state
from config.State import STATE
from utils.logger import set_debug
from probe import probe
from route import (
    restore_routes,
    store_routes,
    switch_default_route,
)


logger = logging.getLogger('Monitor')


class Monitor:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config: MwanConfig = load_config(config_path)
        self.config_mtime = get_config_mtime(config_path)
        set_debug(self.config.general.debug)
        self.down_cnt = 0
        self.up_cnt = 0
        self.state = get_state(self.config)
        self.db_path = config_path.with_suffix('.db')
        store_routes(self.config, self.db_path)
        self.quit: Event = Event()

    def stop(self, signum: int, frame=None):
        self.quit.set()

    def run(self):
        try:
            while not self.quit.is_set():
                self.reload_config()
                self.delegate()

                if self.quit.wait(self.config.probe.delay):
                    break
        except Exception:
            try:
                self.cleanup(unexpected=True)
            except Exception:
                logger.exception(f'clean up failed: {self.db_path}')
            raise
        else:
            self.cleanup()

    def cleanup(self, unexpected=False):
        if self.config.general.restore:
            restore_routes(self.db_path)
            return

        if unexpected:
            logger.warning(f'store routes on unexpected exit: {self.db_path}')
            return

        self.db_path.unlink(missing_ok=True)
        logger.info('restore routes disabled')

    def reload_config(self):
        if not self.config.general.hot_reload:
            return

        mtime = get_config_mtime(self.config_path)
        if mtime is None or mtime == self.config_mtime:
            return

        config = load_config(self.config_path)
        self.config_mtime = mtime

        if (
            config.primary.dev != self.config.primary.dev
            or config.backup.dev != self.config.backup.dev
        ):
            logger.error(
                f'config reload conflict: primary: {self.config.primary.dev} -> {config.primary.dev}, backup: {self.config.backup.dev} -> {config.backup.dev}',
            )
            return

        self.config = config
        set_debug(self.config.general.debug)
        self.down_cnt = 0
        self.up_cnt = 0
        self.state = get_state(self.config)

    def delegate(self):
        current_state = self.current_state()

        try:
            up = probe(self.config, current_state, quit_event=self.quit)
        except Exception:
            logger.exception('probe failed')
            return

        if up is None or self.quit.is_set():
            return

        if current_state == STATE.UNKNOWN:
            return

        if current_state == STATE.PRIMARY:
            if up:
                self.down_cnt = 0
                return

            self.down_cnt += 1
            self.up_cnt = 0
            oughta_down = (
                self.config.probe.fast_failover
                or self.down_cnt >= self.config.probe.down
            )
            if self.down_cnt <= 3:
                logger.debug(
                    f'down_cnt={self.down_cnt} down_threshold={self.config.probe.down}'
                )
            if oughta_down:
                self.switch(STATE.BACKUP)
            return

        if current_state == STATE.BACKUP:
            if not up:
                self.up_cnt = 0
                return

            self.up_cnt += 1
            self.down_cnt = 0
            oughta_up = (
                self.config.probe.fast_failover or self.up_cnt >= self.config.probe.up
            )
            if self.up_cnt <= 3:
                logger.debug(
                    f'up_cnt={self.up_cnt} up_threshold={self.config.probe.up}'
                )
            if oughta_up:
                self.switch(STATE.PRIMARY)
            return

    def current_state(self) -> STATE:
        state = get_state(self.config)
        if state != self.state:
            logger.warning(
                f'state switched externally: {self.state.name} -> {state.name}'
            )
            self.down_cnt = 0
            self.up_cnt = 0
            self.state = state
        return self.state

    def switch(self, expec_state: STATE):
        previous_state = self.state
        switch_default_route(self.config, expec_state)
        current_state = get_state(self.config)
        self.state = current_state
        self.down_cnt = 0
        self.up_cnt = 0

        if current_state != expec_state:
            self.state = STATE.UNKNOWN

        logger.warning(f'state switched: {previous_state.name} -> {current_state.name}')
