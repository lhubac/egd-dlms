# Home Assistant Integration

EGD-DLMS integrates with Home Assistant through MQTT Discovery.

Home Assistant does not need to know where EGD-DLMS runs. It only needs access to the same MQTT broker.

```text
EGD-DLMS
    ↓
MQTT broker
    ↓
Home Assistant MQTT integration
    ↓
MQTT Discovery entities
```

---

# Requirements

- MQTT broker reachable by both EGD-DLMS and Home Assistant
- MQTT integration enabled in Home Assistant
- MQTT Discovery enabled

---

# MQTT configuration

In `config.yaml`:

```yaml
mqtt:
  host: 127.0.0.1
  port: 1883
  username: homeassistant
  password: your_password

topics:
  state: home/egd_meter/state
  availability: home/egd_meter/availability
  discovery_prefix: homeassistant
```

If MQTT runs on another host:

```yaml
mqtt:
  host: 192.168.10.20
  port: 1883
```

---

# Home Assistant setup

In Home Assistant:

```text
Settings
  → Devices & services
  → MQTT
```

Configure the same broker, username and password.

After EGD-DLMS starts, entities should appear automatically.

---

# Typical entities

- Current power import
- Current power export
- L1 power
- L2 power
- L3 power
- Imported energy
- Exported energy
- Tariff
- Relay states
- Disconnect status
- Diagnostic entities

---

# Energy Dashboard

Use these entities:

## Grid consumption

```text
EGD energie odběr celkem
```

## Return to grid

```text
EGD energie dodávka celkem
```

These entities use:

```text
device_class: energy
state_class: total_increasing
unit: kWh
```

---

# Troubleshooting

## No entities appear

Check MQTT Discovery messages:

```bash
docker exec -it mosquitto mosquitto_sub \
  -h 127.0.0.1 \
  -u homeassistant \
  -P 'your_password' \
  -t 'homeassistant/sensor/egd_meter/+/config' \
  -v
```

## No state updates

Check:

```bash
docker logs dlms-listener --tail 50
egd-dlms-status
```

## MQTT authentication errors

Check Mosquitto logs:

```bash
docker logs mosquitto --tail 50
```

Look for:

```text
not authorised
```

If present, verify username and password in both Home Assistant and `config.yaml`.
