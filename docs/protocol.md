# Protocol Notes

## EG.D HAN RS485

Known setup:

- Meter: Sagemcom XT211
- Interface: RS485
- Protocol: DLMS/COSEM
- Mode: Push setup - On Schedule 2 (HAN)
- Direction: meter to customer
- Interval: 60 seconds

## Observed push frame

Current frames are 442 bytes.

Useful COSEM objects start around offset 83.

## Register value

Example:

```text
02 02 00 03 01 00 01 07 00 ff 02 06 00 00 00 f6
