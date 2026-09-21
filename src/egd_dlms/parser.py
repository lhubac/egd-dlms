from egd_dlms.config import OBIS_CONFIG
from egd_dlms.models import CosemObject

# AXDR typové značky používané tímhle meterem pro hodnotu COSEM Register
# atributu (empiricky ověřeno na zachycených rámcích, viz
# project_egd_dlms_power_field_bug.md v Claude memory) -> délka hodnoty v bajtech.
VALUE_TYPE_SIZES = {
    0x06: 4,  # double-long-unsigned (uint32)
    0x05: 4,  # double-long (int32)
    0x12: 2,  # long-unsigned (uint16)
    0x10: 2,  # long (int16)
    0x11: 1,  # unsigned (uint8)
    0x0F: 1,  # integer (int8)
}

# Bezpečnostní strop na "rozumnou" hodnotu podle device_class z obis.yaml.
# RS485/USB spojení občas dodá bitově poškozený rámec (typicky po USB
# re-enumeraci FT232 adaptéru) — bez týhle kontroly se to projeví jako
# hodnoty v řádu milionů/miliard wattů. Lepší takovou hodnotu zahodit
# (pole zůstane na poslední známé hodnotě) než publikovat nesmysl do HA.
MAX_PLAUSIBLE_BY_DEVICE_CLASS = {
    "power": 30_000,        # W — scale je u všech power OBIS kódů 1
    "energy": 100_000_000,  # raw jednotky, scale 0.001 -> až 100 000 kWh
}


class CosemParser:
    def __init__(self, logger):
        self.logger = logger

    def parse(self, data: bytes) -> list[CosemObject]:
        objects: list[CosemObject] = []

        i = 0
        while i < len(data):
            register = self._register_value_at(data, i)
            if register is not None:
                obis_raw, value, consumed = register

                objects.append(
                    CosemObject(
                        class_id=3,
                        logical_name=self._obis_short(obis_raw),
                        full_obis=self._obis_full(obis_raw),
                        attribute=2,
                        value=value,
                    )
                )

                i += consumed
                continue

            if self._looks_like_enum_value(data, i):
                class_id = int.from_bytes(data[i + 2:i + 4], "big")
                obis_raw = data[i + 4:i + 10]

                obj = CosemObject(
                    class_id=class_id,
                    logical_name=self._obis_short(obis_raw),
                    full_obis=self._obis_full(obis_raw),
                    attribute=3,
                    value=data[i + 12],
                )

                objects.append(obj)

                i += 13
                continue

            i += 1

        return objects

    def _register_value_at(self, data: bytes, i: int) -> tuple[bytes, int, int] | None:
        """Zkusí na pozici i najít COSEM Register (class_id=3) záznam.

        Skutečná struktura na tomhle meteru (ověřeno na reálně zachycených
        rámcích, viz project_egd_dlms_power_field_bug.md): 2bajtový class_id
        BEZ obalové značky "02 02" (starší kód ji mylně vyžadoval, takže na
        živých datech skoro nikdy nic nenašel), 6bajtový OBIS kód, 2bajtová
        AXDR typová značka (první bajt vždy 0x02, druhý určuje typ/délku
        hodnoty) a hodnota.

        Vrací None, pokud na pozici i nic nesedí, OBIS kód neznáme (viz
        obis.yaml), nebo hodnota neprojde kontrolou rozumnosti — RS485/USB
        spojení občas dodá bitově poškozený rámec a je lepší takové pole
        zahodit (zůstane na poslední známé hodnotě), než publikovat
        nesmysl (viz MAX_PLAUSIBLE_BY_DEVICE_CLASS).
        """
        if i + 10 > len(data):
            return None
        if data[i] != 0x00 or data[i + 1] != 0x03:
            return None

        obis_raw = data[i + 2:i + 8]
        short = self._obis_short(obis_raw)
        full = self._obis_full(obis_raw)

        mapping = OBIS_CONFIG.get(full) or OBIS_CONFIG.get(short)
        if mapping is None:
            return None

        if data[i + 8] != 0x02:
            return None

        size = VALUE_TYPE_SIZES.get(data[i + 9])
        if size is None or i + 10 + size > len(data):
            return None

        raw_value = int.from_bytes(data[i + 10:i + 10 + size], "big", signed=False)

        if not self._is_plausible(mapping, raw_value):
            self.logger.warning(
                "Zahozena nepravděpodobná hodnota OBIS %s: raw=%s (podezření na poškozený rámec)",
                full, raw_value,
            )
            return None

        return obis_raw, raw_value, 10 + size

    def _is_plausible(self, mapping: dict, raw_value: int) -> bool:
        cap = MAX_PLAUSIBLE_BY_DEVICE_CLASS.get(mapping.get("device_class"))
        if cap is None:
            return True
        return 0 <= raw_value <= cap

    def extract_serial(self, data: bytes) -> str | None:
        # OBIS 0-0:96.1.0.255 (idx 3 v EG.D dokumentaci) — čti hodnotu obecně
        # podle OBIS kódu, ne podle textového prefixu konkrétního výrobce
        # (starší kód hledal natvrdo b"SAG", což fungovalo jen pro Sagemcom).
        value = self._find_data_string(data, "96.1.0")
        if value is not None:
            return value
        # Fallback pro starší/jiné meterové profily se Sagemcom prefixem.
        idx = data.find(b"SAG")
        if idx == -1:
            return None
        return data[idx:idx + 16].decode("ascii", errors="ignore")

    def extract_tariff(self, data: bytes) -> str | None:
        # OBIS 0-0:96.14.0.255 (idx 12 v EG.D dokumentaci) — čti hodnotu obecně
        # podle OBIS kódu. Starší kód hledal natvrdo velká písmena b"T1".."T4",
        # ale meter může posílat i malá písmena (pozorováno "t3"), proto to
        # dřív u tohoto typu meteru nikdy nenašlo shodu.
        value = self._find_data_string(data, "96.14.0")
        if value is not None:
            return value
        # Fallback na starší pevný seznam pro meterové profily bez OBIS shody.
        for tariff in [b"T1", b"T2", b"T3", b"T4", b"t1", b"t2", b"t3", b"t4"]:
            if tariff in data:
                return tariff.decode("ascii")
        return None

    def _find_data_string(self, data: bytes, obis_short_target: str) -> str | None:
        """Projde rámec a hledá class 1 (Data) octet-string objekty podle OBIS kódu.

        Struktura (empiricky ověřeno na živém rámci 2026-08-22):
        02 02 [class_id:2]=00 01 [obis:6] [attribute:1] [axdr_type:1]=0x09 [length:1] [value:length bajtů]
        """
        i = 0
        while i < len(data):
            if self._looks_like_data_string_value(data, i):
                obis_raw = data[i + 4:i + 10]
                length = data[i + 12]
                if self._obis_short(obis_raw) == obis_short_target:
                    value = data[i + 13:i + 13 + length]
                    text = value.decode("ascii", errors="ignore").strip("\x00").strip()
                    return text or None
                i += 13 + length
                continue
            i += 1
        return None

    def _looks_like_data_string_value(self, data: bytes, i: int) -> bool:
        if i + 13 > len(data):
            return False
        if data[i] != 0x02 or data[i + 1] != 0x02:
            return False
        class_id = int.from_bytes(data[i + 2:i + 4], "big")
        if class_id != 1:
            return False
        if data[i + 11] != 0x09:  # AXDR octet-string type tag
            return False
        length = data[i + 12]
        return i + 13 + length <= len(data)

    def _looks_like_enum_value(self, data: bytes, i: int) -> bool:
        if i + 13 > len(data):
            return False

        if data[i] != 0x02 or data[i + 1] != 0x02:
            return False

        class_id = int.from_bytes(data[i + 2:i + 4], "big")

        if class_id not in (70, 71):
            return False

        return data[i + 10] == 0x03 and data[i + 11] == 0x16

    def _obis_short(self, raw: bytes) -> str:
        return f"{raw[2]}.{raw[3]}.{raw[4]}"

    def _obis_full(self, raw: bytes) -> str:
        return f"{raw[0]}-{raw[1]}:{raw[2]}.{raw[3]}.{raw[4]}.{raw[5]}"
