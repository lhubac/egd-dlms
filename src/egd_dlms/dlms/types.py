from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DlmsValue:
    tag: int
    type_name: str
    value: Any


DLMS_TYPES = {
    0x00: "null-data",
    0x01: "array",
    0x02: "structure",
    0x03: "boolean",
    0x05: "double-long",
    0x06: "double-long-unsigned",
    0x09: "octet-string",
    0x0A: "visible-string",
    0x0F: "integer",
    0x10: "long",
    0x11: "unsigned",
    0x12: "long-unsigned",
    0x16: "enum",
}
