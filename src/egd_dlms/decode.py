import sys
from pathlib import Path

from egd_dlms.config import OBIS_CONFIG
from egd_dlms.logger import setup_logger
from egd_dlms.dlms.parser import DlmsPushParser
from egd_dlms.decoder import ObisDecoder


def load_hex_frame(path: Path) -> bytes:
    return bytes.fromhex(path.read_text(encoding="utf-8").strip())


def main():
    logger = setup_logger()

    if len(sys.argv) > 1:
        frame_path = Path(sys.argv[1])
    else:
        frame_path = Path("samples/last_frame.hex")

    frame = load_hex_frame(frame_path)

    parser = DlmsPushParser(logger)
    decoder = ObisDecoder(logger)

    objects = parser.extract_capture_objects_heuristic(frame)

    state = decoder.decode(
        objects=objects,
        serial=None,
        tariff=None,
    )
    def unit_for_key(key: str) -> str:
        for item in OBIS_CONFIG.values():
            if item.get("key") == key:
                return item.get("unit") or ""
        return ""

    print()
    print("Decoded meter values")
    print("=" * 80)

    for key, value in state.values.items():
        unit = unit_for_key(key)
        print(f"{key:30} {value} {unit}".rstrip())

if __name__ == "__main__":
    main()
