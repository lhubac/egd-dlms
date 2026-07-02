import time

from egd_dlms.config import METER
from egd_dlms.decoder import ObisDecoder
from egd_dlms.diagnostics import Diagnostics
from egd_dlms.logger import setup_logger
from egd_dlms.meter import MeterTcpClient
from egd_dlms.mqtt import MqttPublisher
from egd_dlms.parser import CosemParser
from egd_dlms.recorder import FrameRecorder
from egd_dlms.connection_monitor import ConnectionMonitor
from egd_dlms.runtime_state import RuntimeState

def main():
    logger = setup_logger()
    logger.info("EGD DLMS projekt startuje")

    reconnect_delay = int(METER.get("reconnect_delay", 5))

    diagnostics = Diagnostics()
    recorder = FrameRecorder(logger)
    runtime_state = RuntimeState(logger)
    monitor = ConnectionMonitor(logger)

    mqtt = MqttPublisher(logger, on_reconnect=runtime_state.mqtt_reconnect)
    mqtt.connect()

    parser = CosemParser(logger)
    decoder = ObisDecoder(logger)

    while True:
        try:
            monitor.connection_started()
            meter = MeterTcpClient(logger, on_idle=monitor.check)

            for frame in meter.read_frames():
                monitor.frame_received()
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

                runtime_state.frame_received(payload)
                recorder.save(frame, payload)
                mqtt.publish_state(payload)

        except Exception as e:
            diagnostics.reconnect()
            runtime_state.tcp_reconnect()
            logger.error("Spojení s převodníkem selhalo: %s", e)
            logger.info("Nový pokus za %s s", reconnect_delay)
            time.sleep(reconnect_delay)


if __name__ == "__main__":
    main()
