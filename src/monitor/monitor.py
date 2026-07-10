import logging
from threading import Event

from config.Config import MwanConfig
from probe import ping_cycle
from route import apply_route


logger = logging.getLogger("Monitor")


class MwanMonitor:
    def __init__(self, config: MwanConfig) -> None:
        self.config = config
        self.quit = Event()
        self.fail_streak = 0
        self.recover_streak = 0
        self.active_state: str | None = None

    def stop(self, signum: int) -> None:
        logger.info(f"mwan stopping {signum}")
        self.quit.set()

    def run(self, *, once: bool = False) -> None:
        logger.info(
            f"mwan started: primary={self.config.primary.dev} backup={self.config.backup.dev} hosts={','.join(self.config.probe.hosts)}"
        )

        while not self.quit.is_set():
            self.run_once()

            if once:
                break
            if self.quit.wait(self.config.probe.delay):
                break

    def run_once(self) -> None:
        cycle_failed = ping_cycle(self.config)

        if cycle_failed:
            self.fail_streak += 1
            self.recover_streak = 0
            should_fail = (
                self.config.probe.fast_down
                or self.fail_streak >= self.config.probe.down
            )
            logger.info(
                "fail streak: current=%s threshold=%s fast=%s",
                self.fail_streak,
                self.config.probe.down,
                int(self.config.probe.fast_down),
            )
            if should_fail and self.active_state != "DOWN":
                apply_route(self.config, "DOWN")
                self.active_state = "DOWN"
            return

        self.recover_streak += 1
        self.fail_streak = 0
        should_recover = (
            self.config.probe.fast_up or self.recover_streak >= self.config.probe.up
        )
        logger.info(
            "recover streak: current=%s threshold=%s fast=%s",
            self.recover_streak,
            self.config.probe.up,
            int(self.config.probe.fast_up),
        )
        if should_recover and self.active_state != "UP":
            apply_route(self.config, "UP")
            self.active_state = "UP"
