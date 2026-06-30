import time

from egd_dlms.config import METER
from egd_dlms.decoder import ObisDecoder
from egd_dlms.diagnostics import Diagnostics
from egd_dlms.logger import setup_logger
from egd_dlms.meter import MeterTcpClient
from egd_dlms.mqtt import MqttPublisher
from egd_dlms.parser import CosemParser
from egd_dlms.recorder import FrameRecorder


def main():
    logger = setup_logger()
    logger.info("EGD DLMS projekt startuje")

    reconnect_delay = int(METER.get("reconnect_delay", 5))

    diagnostics = Diagnostics()
    recorder = FrameRecorder(logger)

    mqtt = MqttPublisher(logger)
    mqtt.connect()

    parser = CosemParser(logger)
    decoder = ObisDecoder(logger)

    while True:
        try:
            meter = MeterTcpClient(logger)

            for frame in meter.read_frames():
                objects = parser.parse(frame)
                serial = parser.extract_serial(frame)
                tariff = parser.extract_tariff(frame)

                state = decoder.decode(
                    objects=objects,
                    serial=serial,
                    tariff=tariff,
                )

                diag = diagnostics.frame_received(len(frame))
                payload = mqtt.build_payload(state, diag)

                recorder.save(frame, payload)
                mqtt.publish_state(payload)

        except Exception as e:
            diagnostics.reconnect()
            logger.error("Spojení s převodníkem selhalo: %s", e)
            logger.info("Nový pokus za %s s", reconnect_delay)
            time.sleep(reconnect_delay)


if __name__ == "__main__":
    main()
