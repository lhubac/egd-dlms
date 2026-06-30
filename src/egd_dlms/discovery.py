import json

from egd_dlms.config import DEVICE, TOPICS, OBIS_CONFIG


EXTRA_SENSORS = {
    "meter_serial": {
        "name": "EGD výrobní číslo",
    },
    "tariff": {
        "name": "EGD aktuální tarif",
    },
    "last_message": {
        "name": "EGD poslední zpráva",
        "device_class": "timestamp",
    },
    "message_count": {
        "name": "EGD počet zpráv",
        "state_class": "total_increasing",
    },
    "reconnect_count": {
        "name": "EGD počet reconnectů",
        "state_class": "total_increasing",
    },
    "last_frame_length": {
        "name": "EGD délka posledního rámce",
        "unit": "B",
        "device_class": "data_size",
        "state_class": "measurement",
    },
}


def build_device() -> dict:
    return {
        "identifiers": [DEVICE.get("identifier", "egd_sagemcom_xt211")],
        "name": DEVICE.get("name", "EGD elektroměr"),
        "manufacturer": DEVICE.get("manufacturer", "Sagemcom"),
        "model": DEVICE.get("model", "XT211"),
    }


def publish_discovery(client, logger):
    device = build_device()

    sensors = {}

    for _obis, item in OBIS_CONFIG.items():
        key = item["key"]
        sensors[key] = {
            "name": item["name"],
            "unit": item.get("unit"),
            "device_class": item.get("device_class"),
            "state_class": item.get("state_class"),
        }

    sensors.update(EXTRA_SENSORS)

    prefix = TOPICS.get("discovery_prefix", "homeassistant")
    state_topic = TOPICS.get("state", "home/egd_meter/state")
    availability_topic = TOPICS.get("availability", "home/egd_meter/availability")

    for key, sensor in sensors.items():
        topic = f"{prefix}/sensor/egd_meter/{key}/config"

        payload = {
            "name": sensor["name"],
            "unique_id": f"egd_meter_{key}",
            "state_topic": state_topic,
            "availability_topic": availability_topic,
            "value_template": "{{ value_json." + key + " }}",
            "device": device,
        }

        if sensor.get("unit"):
            payload["unit_of_measurement"] = sensor["unit"]
        if sensor.get("device_class"):
            payload["device_class"] = sensor["device_class"]
        if sensor.get("state_class"):
            payload["state_class"] = sensor["state_class"]

        client.publish(topic, json.dumps(payload), qos=0, retain=True)

    logger.info("MQTT Discovery odesláno")
