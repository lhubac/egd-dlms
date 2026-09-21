from egd_dlms.decoder import ObisDecoder
from egd_dlms.models import CosemObject


class DummyLogger:
    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def _objects():
    return [
        CosemObject(class_id=3, logical_name="2.7.0", full_obis="1-0:2.7.0.255", attribute=2, value=224),
        CosemObject(class_id=3, logical_name="22.7.0", full_obis="1-0:22.7.0.255", attribute=2, value=0),
        CosemObject(class_id=3, logical_name="1.7.0", full_obis="1-0:1.7.0.255", attribute=2, value=123),
    ]


def test_export_passthrough_by_default(monkeypatch):
    import egd_dlms.config as cfgmod

    monkeypatch.setitem(cfgmod.METER, "assume_no_export", False)
    decoder = ObisDecoder(DummyLogger())
    assert decoder.assume_no_export is False

    state = decoder.decode(_objects(), serial=None, tariff=None)
    assert state.values["power_export_w"] == 224.0
    assert state.values["power_import_w"] == 123.0


def test_nonzero_export_dropped_when_assume_no_export(monkeypatch):
    import egd_dlms.config as cfgmod

    monkeypatch.setitem(cfgmod.METER, "assume_no_export", True)
    decoder = ObisDecoder(DummyLogger())
    assert decoder.assume_no_export is True

    state = decoder.decode(_objects(), serial=None, tariff=None)
    # nonzero export field dropped entirely (not even set to 0 -- absent,
    # so HA holds the last known-good value instead of flashing a wrong one)
    assert "power_export_w" not in state.values
    # zero export readings still pass through fine
    assert state.values["power_export_l1_w"] == 0.0
    # non-export fields are never touched by this filter
    assert state.values["power_import_w"] == 123.0
