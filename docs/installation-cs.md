# Instalace

Projekt EGD-DLMS lze provozovat několika způsoby.

Na umístění Home Assistantu nezáleží. Jedinou podmínkou je, aby Home Assistant i EGD-DLMS měly přístup ke stejnému MQTT brokeru.

## Podporované varianty

1. Docker Compose na stejném zařízení jako Home Assistant
2. Docker Compose na samostatném zařízení
3. Samostatná instalace pomocí Pythonu
4. Vývojové prostředí

---

# 1. Docker Compose na stejném zařízení

Doporučené řešení pro Raspberry Pi, kde běží Home Assistant, Mosquitto i EGD-DLMS.

## Požadavky

- Linux
- Docker
- Docker Compose
- MQTT broker
- Převodník RS485/TCP připojený k elektroměru

## Konfigurace

Upravte soubor:

```text
config.yaml
```

Příklad:

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
  password: vaše_heslo
```

## Spuštění

```bash
docker compose up -d --build
```

## Ověření

```bash
docker logs -f dlms-listener
```

Měli byste vidět:

```text
MQTT připojeno
Připojeno k převodníku
STATE ...
```

---

# 2. Docker Compose na jiném zařízení

Pokud Home Assistant běží na jiném počítači, nastavte pouze IP adresu MQTT brokeru.

```yaml
mqtt:
  host: 192.168.10.20
  port: 1883
```

Poté spusťte:

```bash
docker compose up -d --build
```

---

# 3. Samostatná Python instalace

Vhodné pro vývoj nebo servery bez Dockeru.

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```

Spuštění:

```bash
egd-dlms
```

Diagnostika:

```bash
egd-dlms-status
```

---

# 4. Vývojové prostředí

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

pytest -v
```

---

# Doporučené nastavení pro produkční provoz

Historii rámců doporučujeme vypnout.

```yaml
recorder:
  enabled: false
  save_last: false
  save_history: false
```

Runtime informace zůstávají aktivní:

```yaml
runtime:
  directory: runtime
  status_file: status.json
```

Stav služby:

```bash
egd-dlms-status
```
