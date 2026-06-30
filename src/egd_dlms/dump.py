import sys
from pathlib import Path

from egd_dlms.dlms.parser import DlmsPushParser


def load_hex_frame(path: Path) -> bytes:
    return bytes.fromhex(path.read_text(encoding="utf-8").strip())


def hexdump(data: bytes, start: int, length: int = 20) -> str:
    part = data[start:start + length]
    return part.hex(" ")


def main():
    if len(sys.argv) > 1:
        frame_path = Path(sys.argv[1])
    else:
        frame_path = Path("samples/last_frame.hex")

    data = load_hex_frame(frame_path)

    parser = DlmsPushParser(logger=None)
    objects = parser.extract_capture_objects_heuristic(data)

    print(f"Soubor: {frame_path}")
    print(f"Délka rámce: {len(data)} B")
    print()
    print("COSEM object dump")
    print("=" * 120)

    for obj in objects:
        print(
            f"offset={obj.offset:03} "
            f"class={obj.class_id:<3} "
            f"attr={obj.attribute_index:<2} "
            f"obis={obj.full_obis:<20} "
            f"value={obj.value:<12} "
            f"raw={hexdump(data, obj.offset, 18)}"
        )


if __name__ == "__main__":
    main()
