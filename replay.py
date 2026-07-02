import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

from logger import setup_logger
from dlms.parser import DlmsPushParser


def load_hex_frame(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8").strip()
    return bytes.fromhex(text)


def main():
    logger = setup_logger()

    if len(sys.argv) > 1:
        frame_path = Path(sys.argv[1])
    else:
        frame_path = Path("tests/data/sample_push_frame.hex")

    if not frame_path.exists():
        raise FileNotFoundError(f"Soubor neexistuje: {frame_path}")

    frame = load_hex_frame(frame_path)

    print(f"Soubor: {frame_path}")
    print(f"Délka rámce: {len(frame)} B")

    parser = DlmsPushParser(logger)

    objects = parser.extract_capture_objects_heuristic(frame)

    print()
    print("Nalezené COSEM objekty:")
    print("-" * 80)

    for obj in objects:
        print(
            f"class={obj.class_id:<3} "
            f"attr={obj.attribute_index:<2} "
            f"obis={obj.full_obis:<20} "
            f"short={obj.logical_name:<10} "
            f"value={obj.value}"
        )

    print()
    print("JSON:")
    print(json.dumps([obj.__dict__ for obj in objects], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
