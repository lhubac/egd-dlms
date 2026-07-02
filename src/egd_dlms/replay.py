from pathlib import Path

from egd_dlms.logger import setup_logger
from egd_dlms.dlms.parser import DlmsPushParser


def main():

    logger = setup_logger()

    frame = Path("tests/data/sample_push_frame.hex").read_text().strip()

    data = bytes.fromhex(frame)

    parser = DlmsPushParser(logger)

    objects = parser.extract_capture_objects_heuristic(data)

    print()

    print("COSEM Objects")

    print("=" * 90)

    for o in objects:

        print(
            f"{o.full_obis:20}"
            f"class={o.class_id:3}"
            f" attr={o.attribute_index}"
            f" value={o.value}"
        )
