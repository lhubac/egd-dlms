from egd_dlms.models import CosemObject


class CosemParser:
    def __init__(self, logger):
        self.logger = logger

    def parse(self, data: bytes) -> list[CosemObject]:
        objects: list[CosemObject] = []

        i = 0
        while i < len(data):
            if self._looks_like_register_value(data, i):
                class_id = int.from_bytes(data[i + 2:i + 4], "big")
                obis_raw = data[i + 4:i + 10]

                objects.append(
                    CosemObject(
                        class_id=class_id,
                        logical_name=self._obis_short(obis_raw),
                        full_obis=self._obis_full(obis_raw),
                        attribute=2,
                        value=int.from_bytes(data[i + 12:i + 16], "big", signed=False),
                    )
                )

                i += 16
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

    def _looks_like_register_value(self, data: bytes, i: int) -> bool:
        return (
            i + 16 <= len(data)
            and data[i] == 0x02
            and data[i + 1] == 0x02
            and int.from_bytes(data[i + 2:i + 4], "big") == 3
            and data[i + 10] == 0x02
            and data[i + 11] == 0x06
        )

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
