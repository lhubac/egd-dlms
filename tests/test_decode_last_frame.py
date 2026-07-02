from pathlib import Path

from egd_dlms.dlms.parser import DlmsPushParser
from egd_dlms.decoder import ObisDecoder


class DummyLogger:
    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def test_decode_last_frame():
    frame_path = Path("tests/data/sample_push_frame.hex")
    assert frame_path.exists(), "Chybí tests/data/sample_push_frame.hex"

    frame = bytes.fromhex(frame_path.read_text(encoding="utf-8").strip())

    logger = DummyLogger()
    parser = DlmsPushParser(logger)
    decoder = ObisDecoder(logger)

    objects = parser.extract_capture_objects_heuristic(frame)
    assert len(objects) == 21
    
    state = decoder.decode(
        objects=objects,
        serial=None,
        tariff=None,
    )

    values = state.values

    assert "power_import_w" in values
    assert "energy_import_kwh" in values
    assert "energy_export_kwh" in values
    assert "disconnect_status" in values
    assert "relay_1_status" in values

    assert values["energy_import_kwh"] > 0
    assert values["energy_export_kwh"] >= 0
    assert values["power_import_w"] >= 0
