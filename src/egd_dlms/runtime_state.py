import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from egd_dlms.config import CONFIG, PROJECT_DIR


class RuntimeState:
    def __init__(self, logger):
        self.logger = logger

        cfg = CONFIG.get("runtime", {})
        directory = cfg.get("directory", "runtime")
        status_file = cfg.get("status_file", "status.json")

        self.runtime_dir = PROJECT_DIR / directory
        self.status_path = self.runtime_dir / status_file
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

        self.started = datetime.now(timezone.utc).isoformat()
        self.frames_received = 0
        self.tcp_reconnects = 0
        self.mqtt_reconnects = 0

        self.logger.info("Runtime state aktivní: %s", self.status_path)

    def frame_received(self, meter_payload: dict[str, Any]) -> None:
        self.frames_received += 1
        self.save(meter_payload)

    def tcp_reconnect(self) -> None:
        self.tcp_reconnects += 1

    def mqtt_reconnect(self) -> None:
        self.mqtt_reconnects += 1

    def build_status(self, meter_payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "runtime": {
                "started": self.started,
                "frames_received": self.frames_received,
                "tcp_reconnects": self.tcp_reconnects,
                "mqtt_reconnects": self.mqtt_reconnects,
            },
            "meter": meter_payload,
        }

    def save(self, meter_payload: dict[str, Any]) -> None:
        status = self.build_status(meter_payload)
        tmp_path = self.status_path.with_suffix(".json.tmp")

        try:
            tmp_path.write_text(
                json.dumps(status, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            tmp_path.replace(self.status_path)
        except Exception as e:
            self.logger.warning("Uložení runtime state selhalo: %s", e)
