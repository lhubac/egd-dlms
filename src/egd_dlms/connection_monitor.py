import time

from egd_dlms.config import CONFIG


class ConnectionMonitor:
    def __init__(self, logger):
        cfg = CONFIG.get("watchdog", {})

        self.logger = logger
        self.enabled = bool(cfg.get("enabled", True))
        self.warning_after = int(cfg.get("warning_after_seconds", 180))
        self.reconnect_after = int(cfg.get("reconnect_after_seconds", 600))

        self.last_frame_time = time.time()
        self.warning_logged = False

    def frame_received(self) -> None:
        self.last_frame_time = time.time()
        self.warning_logged = False

    def connection_started(self) -> None:
        self.last_frame_time = time.time()
        self.warning_logged = False

    def check(self) -> None:
        if not self.enabled:
            return

        age = time.time() - self.last_frame_time

        if age >= self.warning_after and not self.warning_logged:
            self.logger.warning(
                "Connection monitor: poslední rámec přišel před %.0f s",
                age,
            )
            self.warning_logged = True

        if age >= self.reconnect_after:
            raise TimeoutError(
                f"Connection monitor: rámec nepřišel {age:.0f} s, vynucuji reconnect"
            )
