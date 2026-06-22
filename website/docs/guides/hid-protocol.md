---
sidebar_position: 2
title: HID Protocol
---

# HID Protocol

The Luxafor Flag communicates over USB HID (Human Interface Device). This page documents the protocol used for direct USB control.

## Device identification

| Property | Value |
|---|---|
| Vendor ID | `0x04D8` (Microchip Technology) |
| Product ID | `0xF372` |
| Report size | 8 bytes |

## Report format

Each HID write sends an 8-byte report:

```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│  Byte 0  │  Byte 1  │  Byte 2  │  Byte 3  │  Byte 4  │  Byte 5  │  Byte 6  │  Byte 7  │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Report ID│ Reserved │  Color   │ Reserved │ Reserved │ Reserved │ Reserved │ Reserved │
│   0x00   │   0x00   │  (enum)  │   0x00   │   0x00   │   0x00   │   0x00   │   0x00   │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

Only bytes 0 and 2 carry meaningful data in the basic color-set command.

## Color codes

Each color maps to an ASCII character code:

| Color | Hex | ASCII | Decimal |
|---|---|---|---|
| Off | `0x4F` | `O` | 79 |
| Red | `0x52` | `R` | 82 |
| Green | `0x47` | `G` | 71 |
| Blue | `0x42` | `B` | 66 |
| Cyan | `0x43` | `C` | 67 |
| Magenta | `0x4D` | `M` | 77 |
| Yellow | `0x59` | `Y` | 89 |
| White | `0x57` | `W` | 87 |

The color byte is the ASCII value of the first letter of the color name (uppercase), except for Off which uses `O`.

## HIDBuffer class

The `HIDBuffer` class wraps the 8-byte report:

```python
from luxafor.local import HIDBuffer, FlagColor

buf = HIDBuffer(report_id=0x00, color=FlagColor.RED)
bytes(buf)  # b'\x00\x00R\x00\x00\x00\x00\x00'
len(buf)    # 8
buf[2]      # 82 (0x52)
```

`HIDBuffer` supports indexing, iteration, `len()`, `bytes()`, `in`, and `repr()`.

## LuxaforFlag class

The `LuxaforFlag` class manages the USB connection and color writes:

```python
from luxafor.local import LuxaforFlag, FlagColor

flag = LuxaforFlag()       # connects to the device on init
flag.set_color(FlagColor.RED)   # writes the 8-byte HID report
flag.set_color(FlagColor.OFF)   # turns the LED off
```

### Connection behavior

- `__init__` immediately calls `connect()`, which opens the HID device
- If the device is not found, `connect()` catches the exception and sets `device = None`
- `set_color()` attempts to reconnect if `device` is `None`
- A failed write resets `device` to `None` for the next call to retry

### Error handling

All HID errors are caught and logged via loguru. No exceptions propagate to the caller — the driver is designed for fire-and-forget usage in the monitor loop.
