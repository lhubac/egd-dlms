from typing import Any

from egd_dlms.config import OBIS_CONFIG
from egd_dlms.models import CosemObject, MeterState


class ObisDecoder:
    def __init__(self, logger):
        self.logger = logger

    def decode(
        self,
        objects: list[CosemObject],
        serial: str | None = None,
        tariff: str | None = None,
    ) -> MeterState:
        values: dict[str, Any] = {}

        if serial:
            values["meter_serial"] = serial

        if tariff:
            values["tariff"] = tariff

        for obj in objects:
            mapping = OBIS_CONFIG.get(obj.full_obis) or OBIS_CONFIG.get(obj.logical_name)

            if not mapping:
                continue

            attribute = getattr(obj, "attribute", None)
            if attribute is None:
                attribute = getattr(obj, "attribute_index", None)

            if attribute not in (2, 3):
                continue

            key = mapping["key"]

            enum_map = mapping.get("enum_map")
            if enum_map:
                values[key] = enum_map.get(obj.value, str(obj.value))
                continue

            scale = float(mapping.get("scale", 1))
            values[key] = round(obj.value * scale, 3)

        return MeterState(values=values)
