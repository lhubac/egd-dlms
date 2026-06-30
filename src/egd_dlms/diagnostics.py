from typing import Any


class Diagnostics:
    def __init__(self):
        self.message_count = 0
        self.reconnect_count = 0
        self.last_frame_length = 0

    def frame_received(self, frame_length: int) -> dict[str, Any]:
        self.message_count += 1
        self.last_frame_length = frame_length

        return {
            "last_message": None,
            "message_count": self.message_count,
            "reconnect_count": self.reconnect_count,
            "last_frame_length": self.last_frame_length,
        }

    def reconnect(self):
        self.reconnect_count += 1
