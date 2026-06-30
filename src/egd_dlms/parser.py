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

                self.logger.info(
                    "ENUM object: class=%s logical=%s full=%s attr=%s value=%s",
                    obj.class_id,
                    obj.logical_name,
                    obj.full_obis,
                    obj.attribute,
                    obj.value,
                )

                i += 13
                continue

            i += 1

        return objects

    def extract_serial(self, data: bytes) -> str | None:
        idx = data.find(b"SAG")
        if idx == -1:
            return None
        return data[idx:idx + 16].decode("ascii", errors="ignore")

    def extract_tariff(self, data: bytes) -> str | None:
        for tariff in [b"T1", b"T2", b"T3", b"T4"]:
            if tariff in data:
                return tariff.decode("ascii")
        return None

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
