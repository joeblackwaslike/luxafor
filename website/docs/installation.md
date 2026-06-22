---
sidebar_position: 2
title: Installation
---

# Installation

## Requirements

- Python 3.12+
- A [Luxafor Flag](https://luxafor.com/luxafor-flag/) USB device (for local HID control)
- macOS or Linux (the `hid` package requires HID API access)

## Install from source

```bash
git clone https://github.com/joeblackwaslike/luxafor.git
cd luxafor
uv sync
```

This installs all dependencies and makes the `luxafor` CLI available in the virtual environment.

## Verify the installation

```bash
uv run luxafor --help
```

You should see the available commands: `set-color` and `monitor`.

## USB permissions

The Luxafor Flag uses USB HID. On Linux, you may need a udev rule to access the device without root:

```bash
# /etc/udev/rules.d/99-luxafor.rules
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="f372", MODE="0666"
```

Reload udev after creating the rule:

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

On macOS, no additional permissions are needed — HID access works out of the box.

## Dependencies

| Package | Purpose |
|---|---|
| [hid](https://pypi.org/project/hid/) | USB HID communication |
| [anyio](https://pypi.org/project/anyio/) | Async runtime for the monitor |
| [httpx](https://pypi.org/project/httpx/) | Async HTTP client for webhooks |
| [furl](https://pypi.org/project/furl/) | URL construction |
| [typer](https://pypi.org/project/typer/) | CLI framework |
| [loguru](https://pypi.org/project/loguru/) | Structured logging |
