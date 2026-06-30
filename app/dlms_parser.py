from obis import OBIS_MAP


def obis_to_string(raw: bytes) -> str:
    return f"{raw[2]}.{raw[3]}.{raw[4]}"


def parse_dlms_payload(data: bytes) -> dict:
    result = {}

    idx = data.find(b"SAG")
    if idx != -1:
        result["meter_serial"] = data[idx:idx + 16].decode("ascii", errors="ignore")

    for tariff in [b"T1", b"T2", b"T3", b"T4"]:
        if tariff in data:
            result["tariff"] = tariff.decode("ascii")

    i = 0

    while i < len(data) - 16:
        if (
            data[i] == 0x02
            and data[i + 1] == 0x02
            and data[i + 2] == 0x00
            and data[i + 3] == 0x03
            and data[i + 10] == 0x02
            and data[i + 11] == 0x06
        ):
            obis = obis_to_string(data[i + 4:i + 10])
            value_raw = int.from_bytes(data[i + 12:i + 16], "big", signed=False)

            if obis in OBIS_MAP:
                key, scale = OBIS_MAP[obis]
                result[key] = round(value_raw * scale, 3)

            i += 16
        else:
            i += 1

    return result
