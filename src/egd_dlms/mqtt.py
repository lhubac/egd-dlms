import json
import time

import paho.mqtt.client as mqtt

from egd_dlms.config import MQTT, TOPICS
from egd_dlms.discovery import publish_discovery
from egd_dlms.models import MeterState


class MqttPublisher:
    def __init__(self, logger):
        self.logger = logger
        self.state_topic = TOPICS.get("state", "home/egd_meter/state")
        self.availability_topic = TOPICS.get("availability", "home/egd_meter/availability")

        self.qos = int(MQTT.get("qos", 0))
        self.retain = bool(MQTT.get("retain", False))

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.will_set(self.availability_topic, "offline", retain=True)

        username = MQTT.get("username", "")
        password = MQTT.get("password", "")

        if username:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def connect(self):
        host = MQTT.get("host", "127.0.0.1")
        port = int(MQTT.get("port", 1883))

        while True:
            try:
                self.logger.info("Připojuji MQTT %s:%s", host, port)
                self.client.connect(host, port, 60)
                self.client.loop_start()
                return
            except Exception as e:
                self.logger.error("MQTT připojení selhalo: %s", e)
                time.sleep(5)

    def build_payload(self, state: MeterState, diagnostics: dict):
        diagnostics = dict(diagnostics)
        diagnostics["last_message"] = state.timestamp
        return state.to_payload(diagnostics)

    def publish_state(self, payload: dict):
        self.logger.info("STATE: %s", json.dumps(payload, ensure_ascii=False))
        self.client.publish(
            self.state_topic,
            json.dumps(payload),
            qos=self.qos,
            retain=self.retain,
        )    
 
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if str(reason_code) != "Success":
            self.logger.error("MQTT připojení odmítnuto: %s", reason_code)
            return

        self.logger.info("MQTT připojeno")
        client.publish(self.availability_topic, "online", retain=True)
        publish_discovery(client, self.logger)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.logger.warning("MQTT odpojeno: %s", reason_code)
