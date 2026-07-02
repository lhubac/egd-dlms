import json
from datetime import datetime, timezone
from pathlib import Path

from egd_dlms.config import CONFIG, PROJECT_DIR


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_age(timestamp: datetime | None) -> str:
    if not timestamp:
        return "unknown"

    now = datetime.now(timezone.utc)
    age = now - timestamp

    seconds = int(age.total_seconds())

    if seconds < 60:
        return f"{seconds} s ago"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min ago"

    hours = minutes // 60
    return f"{hours} h ago"


def format_uptime(start: str | None) -> str:
    if not start:
        return "unknown"

    try:
        started = datetime.fromisoformat(start)
    except Exception:
        return "unknown"

    delta = datetime.now(timezone.utc) - started

    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    if days:
        return f"{days}d {hours}h {minutes}m"

    return f"{hours}h {minutes}m"

def main():
    recorder_cfg = CONFIG.get("recorder", {})
    watchdog_cfg = CONFIG.get("watchdog", {})
    samples_dir = PROJECT_DIR / recorder_cfg.get("directory", "samples")

    runtime_cfg = CONFIG.get("runtime", {})
    runtime_dir = PROJECT_DIR / runtime_cfg.get("directory", "runtime")
    last_state_path = runtime_dir / runtime_cfg.get("status_file", "status.json")
    last_frame_path = samples_dir / "last_frame.hex"

    status = load_json(last_state_path)

    runtime = status.get("runtime", {})
    state = status.get("meter", status)

    timestamp = parse_timestamp(state.get("timestamp"))
    last_message = parse_timestamp(state.get("last_message"))

    frame_size = "unknown"
    if last_frame_path.exists():
        frame_size = f"{len(bytes.fromhex(last_frame_path.read_text(encoding='utf-8').strip()))} B"

    print()
    print("EGD-DLMS Status")
    print("=" * 50)
    print(f"Uptime ............. {format_uptime(runtime.get('started'))}")
    print(f"Frames received .... {runtime.get('frames_received', 'unknown')}")
    print(f"TCP reconnects ..... {runtime.get('tcp_reconnects', 'unknown')}")
    print(f"MQTT reconnects .... {runtime.get('mqtt_reconnects', 'unknown')}")
    print(f"Project dir ........ {PROJECT_DIR}")
    print(f"Runtime state file . {'yes' if last_state_path.exists() else 'no'}")
    print(f"Recorder ........... {'enabled' if recorder_cfg.get('enabled') else 'disabled'}")
    print(f"Samples dir ........ {samples_dir}")
    print(f"Last frame file .... {'yes' if last_frame_path.exists() else 'no'}")
    print(f"Last state file .... {'yes' if last_state_path.exists() else 'no'}")
    print()
    print(f"Last message ....... {state.get('last_message', 'unknown')}")
    print(f"Last message age ... {format_age(last_message or timestamp)}")
    print(f"Frame size ......... {frame_size}")
    print(f"Message count ...... {state.get('message_count', 'unknown')}")
    print(f"Reconnect count .... {state.get('reconnect_count', 'unknown')}")
    print()
    print(f"Watchdog ........... {'enabled' if watchdog_cfg.get('enabled') else 'disabled'}")
    print(f"Watchdog warning ... {watchdog_cfg.get('warning_after_seconds', 'unknown')} s")
    print(f"Watchdog reconnect . {watchdog_cfg.get('reconnect_after_seconds', 'unknown')} s")
    print()
    print(f"Meter serial ....... {state.get('meter_serial', 'unknown')}")
    print(f"Tariff ............. {state.get('tariff', 'unknown')}")
    print(f"Power import ....... {state.get('power_import_w', 'unknown')} W")
    print(f"Energy import ...... {state.get('energy_import_kwh', 'unknown')} kWh")
    print(f"Energy export ...... {state.get('energy_export_kwh', 'unknown')} kWh")
    print(f"Disconnect status .. {state.get('disconnect_status', 'unknown')}")
    print()


if __name__ == "__main__":
    main()
