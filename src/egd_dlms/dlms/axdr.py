from dataclasses import dataclass, field
from typing import Any


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


@dataclass(slots=True)
class AxdrNode:
    tag: int
    type_name: str
    value: Any = None
    children: list["AxdrNode"] = field(default_factory=list)

    def pretty(self, indent: int = 0) -> str:
        pad = "  " * indent

        if self.children:
            lines = [f"{pad}{self.type_name}"]
            for child in self.children:
                lines.append(child.pretty(indent + 1))
            return "\n".join(lines)

        if isinstance(self.value, bytes):
            value = self.value.hex(" ")
        else:
            value = self.value

        return f"{pad}{self.type_name}: {value}"


class AxdrReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def remaining(self) -> int:
        return len(self.data) - self.pos

    def read_u8(self) -> int:
        if self.pos >= len(self.data):
            raise EOFError("Neočekávaný konec dat")
        value = self.data[self.pos]
        self.pos += 1
        return value

    def read_bytes(self, length: int) -> bytes:
        if self.pos + length > len(self.data):
            raise EOFError("Neočekávaný konec dat")
        value = self.data[self.pos:self.pos + length]
        self.pos += length
        return value

    def read_length(self) -> int:
        first = self.read_u8()

        if first < 0x80:
            return first

        count = first & 0x7F
        return int.from_bytes(self.read_bytes(count), "big")

    def read_node(self) -> AxdrNode:
        tag = self.read_u8()
        type_name = DLMS_TYPES.get(tag, f"unknown-0x{tag:02x}")

        if tag == 0x00:
            return AxdrNode(tag, type_name, None)

        if tag in (0x01, 0x02):
            count = self.read_length()
            node = AxdrNode(tag, f"{type_name}({count})")
            node.children = [self.read_node() for _ in range(count)]
            return node

        if tag == 0x03:
            return AxdrNode(tag, type_name, bool(self.read_u8()))

        if tag == 0x05:
            return AxdrNode(tag, type_name, int.from_bytes(self.read_bytes(4), "big", signed=True))

        if tag == 0x06:
            return AxdrNode(tag, type_name, int.from_bytes(self.read_bytes(4), "big", signed=False))

        if tag == 0x09:
            length = self.read_length()
            return AxdrNode(tag, type_name, self.read_bytes(length))

        if tag == 0x0A:
            length = self.read_length()
            return AxdrNode(tag, type_name, self.read_bytes(length).decode("ascii", errors="ignore"))

        if tag == 0x0F:
            return AxdrNode(tag, type_name, int.from_bytes(self.read_bytes(1), "big", signed=True))

        if tag == 0x10:
            return AxdrNode(tag, type_name, int.from_bytes(self.read_bytes(2), "big", signed=True))

        if tag == 0x11:
            return AxdrNode(tag, type_name, self.read_u8())

        if tag == 0x12:
            return AxdrNode(tag, type_name, int.from_bytes(self.read_bytes(2), "big", signed=False))

        if tag == 0x16:
            return AxdrNode(tag, type_name, self.read_u8())

        raise ValueError(f"Nepodporovaný AXDR typ 0x{tag:02x} na pozici {self.pos - 1}")
