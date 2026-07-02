# Integrace s Home Assistantem

EGD-DLMS komunikuje s Home Assistantem pomocí MQTT Discovery.

Na tom, kde EGD-DLMS běží, nezáleží. Důležité je pouze to, aby Home Assistant i EGD-DLMS používaly stejný MQTT broker.

```
Elektroměr
      │
      ▼
EGD-DLMS
      │
      ▼
MQTT broker
      │
      ▼
Home Assistant
```

---

# Požadavky

- MQTT broker
- Zapnutá MQTT integrace v Home Assistantu
- Zapnuté MQTT Discovery

---

# Konfigurace

Soubor:

```text
config.yaml
```

```yaml
mqtt:
  host: 127.0.0.1
  port: 1883
  username: homeassistant
  password: vaše_heslo
```

Pokud MQTT běží jinde:

```yaml
mqtt:
  host: 192.168.10.20
```

---

# Přidání do Home Assistantu

V Home Assistantu otevřete:

```
Nastavení
 → Zařízení a služby
 → MQTT
```

Připojte se ke stejnému brokeru.

Po spuštění EGD-DLMS se zařízení objeví automaticky.

---

# Dostupné entity

Projekt vytváří například:

- Okamžitý odběr
- Okamžitá dodávka
- Výkon L1
- Výkon L2
- Výkon L3
- Celková odebraná energie
- Celková dodaná energie
- Tarif
- Stav relé
- Stav připojení elektroměru

---

# Energy Dashboard

Použijte entity:

## Odběr ze sítě

```
EGD energie odběr celkem
```

## Dodávka do sítě

```
EGD energie dodávka celkem
```

Tyto entity používají:

```
device_class: energy
state_class: total_increasing
unit: kWh
```

---

# Řešení problémů

## Nezobrazují se entity

Zkontrolujte Discovery:

```bash
docker logs dlms-listener
```

a

```bash
egd-dlms-status
```

---

## Neaktualizují se hodnoty

Ověřte:

- spojení s MQTT
- spojení s převodníkem
- stáří poslední zprávy

```bash
egd-dlms-status
```

---

## Chyba přihlášení k MQTT

Zkontrolujte log Mosquitto:

```bash
docker logs mosquitto
```

Pokud se objevuje:

```
not authorised
```

zkontrolujte uživatelské jméno a heslo v `config.yaml` i v Home Assistantu.
