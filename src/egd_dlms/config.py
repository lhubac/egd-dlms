from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    here = Path(__file__).resolve()

    candidates = [
        Path.cwd(),
        here.parent,
        here.parent.parent,
        here.parent.parent.parent,
    ]

    for path in candidates:
        if (path / "config.yaml").exists() and (path / "obis.yaml").exists():
            return path

    raise FileNotFoundError("Nenalezen config.yaml / obis.yaml")


PROJECT_DIR = project_root()
CONFIG_FILE = PROJECT_DIR / "config.yaml"
OBIS_FILE = PROJECT_DIR / "obis.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


CONFIG = load_yaml(CONFIG_FILE)
OBIS_CONFIG = load_yaml(OBIS_FILE)

METER = CONFIG.get("meter", {})
MQTT = CONFIG.get("mqtt", {})
TOPICS = CONFIG.get("topics", {})
DEVICE = CONFIG.get("device", {})
LOGGING = CONFIG.get("logging", {})
RECORDER = CONFIG.get("recorder", {})
