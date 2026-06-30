import json
from datetime import datetime
from pathlib import Path
from typing import Any

from egd_dlms.config import CONFIG, PROJECT_DIR


class FrameRecorder:
    def __init__(self, logger):
        self.logger = logger

        recorder_cfg = CONFIG.get("recorder", {})

        self.enabled = bool(recorder_cfg.get("enabled", False))
        self.save_last = bool(recorder_cfg.get("save_last", True))
        self.save_history = bool(recorder_cfg.get("save_history", False))

        base_dir = Path(__file__).resolve().parent
#        project_dir = base_dir.parent
#        project_dir = Path("/app")

        directory = recorder_cfg.get("directory", "samples")
        self.samples_dir = PROJECT_DIR / directory

        if self.enabled:
            self.samples_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Frame recorder aktivní: %s", self.samples_dir)

    def save(self, frame: bytes, state_payload: dict[str, Any]) -> None:
        if not self.enabled:
            return

        try:
            if self.save_last:
                self._save_last(frame, state_payload)

            if self.save_history:
                self._save_history(frame, state_payload)

        except Exception as e:
            self.logger.warning("Uložení rámce selhalo: %s", e)

    def _save_last(self, frame: bytes, state_payload: dict[str, Any]) -> None:
        (self.samples_dir / "last_frame.hex").write_text(
            frame.hex(" "),
            encoding="utf-8",
        )

        (self.samples_dir / "last_state.json").write_text(
            json.dumps(state_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _save_history(self, frame: bytes, state_payload: dict[str, Any]) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        (self.samples_dir / f"{stamp}.hex").write_text(
            frame.hex(" "),
            encoding="utf-8",
        )

        (self.samples_dir / f"{stamp}.json").write_text(
            json.dumps(state_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
