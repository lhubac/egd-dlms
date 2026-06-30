from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CosemCaptureObject:
    offset: int
    class_id: int
    full_obis: str
    logical_name: str
    attribute_index: int
    data_index: int
    value: Any


def obis_full(raw: bytes) -> str:
    return f"{raw[0]}-{raw[1]}:{raw[2]}.{raw[3]}.{raw[4]}.{raw[5]}"


def obis_short(raw: bytes) -> str:
    return f"{raw[2]}.{raw[3]}.{raw[4]}"
