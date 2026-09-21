from typing import Any

from egd_dlms.config import METER, OBIS_CONFIG
from egd_dlms.models import CosemObject, MeterState


class ObisDecoder:
    def __init__(self, logger):
        self.logger = logger
        # Instalace bez fotovoltaiky/baterie nikdy nemůže reálně dodávat
        # proud do sítě - jakékoliv nenulové čtení "dodávka"/export pole
        # (OBIS s `is_export: true` v obis.yaml) je proto jistě chybné
        # čtení (heuristický parser občas false-positive matchne vzor na
        # poškozeném rámci, viz memory project_egd_dlms_power_field_bug.md),
        # ne reálná hodnota - takový záznam raději zahodíme, než abychom ho
        # nechali "viset" jako aktuální stav (MQTT payload posílá jen
        # přítomná pole, chybějící pole = HA podrží poslední platnou
        # hodnotu). Default False, ať se chování nezmění pro instalace,
        # co export skutečně mají (FVE/baterie) - je to opt-in přes
        # `meter.assume_no_export: true` v configu.
        self.assume_no_export = bool(METER.get("assume_no_export", False))

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
            value = round(obj.value * scale, 3)

            if self.assume_no_export and mapping.get("is_export") and value != 0:
                self.logger.warning(
                    "Zahozeno nesmyslné čtení '%s'=%s (dodávka do sítě, ale "
                    "assume_no_export=true) - podezření na poškozený rámec",
                    key, value,
                )
                continue

            values[key] = value

        return MeterState(values=values)
