import socket
import time
from collections.abc import Generator

from egd_dlms.config import METER


class MeterTcpClient:
    def __init__(self, logger):
        self.logger = logger

    def read_frames(self) -> Generator[bytes, None, None]:
        host = METER["host"]
        port = int(METER["port"])
        frame_gap = float(METER.get("frame_gap", 0.8))

        self.logger.info("Připojuji se k převodníku %s:%s", host, port)

        with socket.create_connection((host, port), timeout=15) as sock:
            self.logger.info("Připojeno k převodníku")
            sock.settimeout(0.2)

            buffer = b""
            last_data_time = None

            while True:
                try:
                    data = sock.recv(4096)

                    if not data:
                        raise ConnectionError("Převodník ukončil spojení")

                    buffer += data
                    last_data_time = time.time()

                except socket.timeout:
                    if buffer and last_data_time:
                        if time.time() - last_data_time >= frame_gap:
                            frame = buffer
                            buffer = b""
                            last_data_time = None
                            yield frame
