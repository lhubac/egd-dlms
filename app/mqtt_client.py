import json
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from config import MQTT, TOPICS
from discovery import publish_discovery


class EmdMqttClient:
    def __init__(self, logger):
        self.logger = logger
        self.message_count = 0
        self.reconnect_count = 0

        self.state_topic = TOPICS.get("state", "home/egd_meter/state")
        self.availability_topic = TOPICS.get("availability", "home/egd_meter/availability")

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.will_set(self.availability_topic, "offline", retain=True)

        username = MQTT.get("username", "")
        password = MQTT.get("password", "")

        if username:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def now_iso(self):
        return datetime.now(timezone.utc).isoformat()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.logger.info("MQTT připojeno: %s", reason_code)
        client.publish(self.availability_topic, "online", retain=True)
        publish_discovery(client)
        self.logger.info("MQTT Discovery odesláno")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.reconnect_count += 1
        self.logger.warning("MQTT odpojeno: %s", reason_code)

    def connect(self):
        host = MQTT.get("host", "127.0.0.1")
        port = int(MQTT.get("port", 1883))

        while True:
            try:
                self.client.connect(host, port, 60)
                self.client.loop_start()
                return
            except Exception as e:
                self.logger.error("MQTT připojení selhalo: %s", e)
                time.sleep(5)

    def publish_state(self, parsed: dict, frame_length: int):
        self.message_count += 1
        timestamp = self.now_iso()

        payload = {
            "timestamp": timestamp,
            "last_message": timestamp,
            "message_count": self.message_count,
            "reconnect_count": self.reconnect_count,
            "last_frame_length": frame_length,
            **parsed,
        }

        self.logger.info("STATE: %s", json.dumps(payload, ensure_ascii=False))
        self.client.publish(self.state_topic, json.dumps(payload), qos=0, retain=False)
