from egd_dlms.dlms.cosem import CosemCaptureObject, obis_full, obis_short


class DlmsPushParser:
    def __init__(self, logger):
        self.logger = logger

    def extract_capture_objects_heuristic(self, data: bytes) -> list[CosemCaptureObject]:
        """
        Stabilní produkční parser.
        Skenuje celý rámec a hledá známé COSEM objekty.
        """
        objects: list[CosemCaptureObject] = []

        i = 0
        while i < len(data):
            if self._register_value(data, i):
                raw = data[i + 4:i + 10]

                objects.append(
                    CosemCaptureObject(
                        offset=i,
                        class_id=3,
                        full_obis=obis_full(raw),
                        logical_name=obis_short(raw),
                        attribute_index=2,
                        data_index=0,
                        value=int.from_bytes(data[i + 12:i + 16], "big", signed=False),
                    )
                )

                i += 16
                continue

            if self._enum_value(data, i):
                class_id = int.from_bytes(data[i + 2:i + 4], "big")
                raw = data[i + 4:i + 10]

                objects.append(
                    CosemCaptureObject(
                        offset=i,
                        class_id=class_id,
                        full_obis=obis_full(raw),
                        logical_name=obis_short(raw),
                        attribute_index=3,
                        data_index=0,
                        value=data[i + 12],
                    )
                )

                i += 13
                continue

            i += 1

        return objects

    def extract_capture_objects_axdr_experimental(self, data: bytes) -> list[CosemCaptureObject]:
        """
        Budoucí AXDR parser.
        Zatím vrací produkční výsledek, dokud nebude AXDR vrstva hotová.
        """
        return self.extract_capture_objects_heuristic(data)

    def _register_value(self, data: bytes, i: int) -> bool:
        return (
            i + 16 <= len(data)
            and data[i] == 0x02
            and data[i + 1] == 0x02
            and int.from_bytes(data[i + 2:i + 4], "big") == 3
            and data[i + 10] == 0x02
            and data[i + 11] == 0x06
        )

    def _enum_value(self, data: bytes, i: int) -> bool:
        return (
            i + 13 <= len(data)
            and data[i] == 0x02
            and data[i + 1] == 0x02
            and int.from_bytes(data[i + 2:i + 4], "big") in (70, 71)
            and data[i + 10] == 0x03
            and data[i + 11] == 0x16
        )
