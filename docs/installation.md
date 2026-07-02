# Installation

EGD-DLMS can run in several environments.  
Home Assistant does not need to run on the same device. The only requirement is that EGD-DLMS and Home Assistant can both access the same MQTT broker.

## Supported scenarios

1. Docker Compose on the same host as Home Assistant
2. Docker Compose on a separate device
3. Native Python service
4. Development installation

---

# 1. Docker Compose on the same host

Recommended for Raspberry Pi installations where Home Assistant, Mosquitto and EGD-DLMS run together.

## Requirements

- Linux host
- Docker
- Docker Compose
- MQTT broker
- RS485/TCP converter connected to the smart meter

## Configuration

Edit:

```bash
config.yaml
```

Example:

```yaml
meter:
  host: 192.168.10.4
  port: 10001
  frame_gap: 0.8
  reconnect_delay: 5

mqtt:
  host: 127.0.0.1
  port: 1883
  username: homeassistant
  password: your_password
  qos: 1
  retain: false
```

## Start

```bash
docker compose up -d --build
```

## Verify

```bash
docker logs -f dlms-listener
```

Expected:

```text
MQTT připojeno
Připojeno k převodníku
STATE: ...
```

---

# 2. Docker Compose on a separate device

Use this when EGD-DLMS runs on a different Raspberry Pi or server than Home Assistant.

## MQTT configuration

Set MQTT host to the IP address of the MQTT broker used by Home Assistant.

```yaml
mqtt:
  host: 192.168.10.20
  port: 1883
  username: homeassistant
  password: your_password
```

## Start

```bash
docker compose up -d --build
```

## Verify MQTT connection

```bash
docker logs dlms-listener --tail 50
```

Home Assistant should automatically discover entities through MQTT Discovery.

---

# 3. Native Python service

Useful for development or systems without Docker.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```

## Run

```bash
egd-dlms
```

## CLI tools

```bash
egd-dlms-status
egd-dlms-replay
egd-dlms-decode
```

---

# 4. Development installation

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
pytest -v
```

---

# Production recorder settings

For production use, frame history should normally be disabled:

```yaml
recorder:
  enabled: false
  directory: samples
  save_last: false
  save_history: false
```

Runtime status is stored separately and remains active:

```yaml
runtime:
  directory: runtime
  status_file: status.json
```

Check status:

```bash
egd-dlms-status
```
