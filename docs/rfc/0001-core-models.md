# RFC-0001: Core Models

## Status

Draft

## Motivation

The current implementation passes raw `bytes` and dictionaries between modules.
This makes the parser, decoder and publishers tightly coupled.

## Goal

Introduce stable internal data models:

- `DlmsFrame`
- `ObisCode`
- `CosemCaptureObject`
- `RegisterValue`
- `MeterState`

## Non-goals

This RFC does not replace the production parser.

## Proposed design

### DlmsFrame

Represents one received frame and metadata.

### ObisCode

Typed representation of an OBIS code.

### CosemCaptureObject

Represents one COSEM object extracted from a DLMS Push message.

### MeterState

Represents decoded meter state independent of MQTT or Home Assistant.

## Migration

1. Add models without changing runtime behavior.
2. Add tests.
3. Convert decoder to use the models.
4. Keep MQTT publisher as serialization-only layer.

## Done criteria

- Existing tests pass.
- `egd-dlms-replay` still works.
- `egd-dlms-decode` still works.
- Docker listener still publishes valid MQTT state.
