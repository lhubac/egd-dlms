# Architecture

EGD-DLMS is structured as layered software.

## Layers

```text
Transport
  TCP
  Serial
  Optical

Protocol
  HDLC
  LLC
  APDU
  AXDR
  COSEM

DLMS Application
  Push Notification
  GET
  SET
  OBIS Decoder

Integrations
  MQTT
  Home Assistant
  CLI
  InfluxDB
  Prometheus
