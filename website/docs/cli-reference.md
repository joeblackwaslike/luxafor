---
sidebar_position: 4
title: CLI Reference
---

# CLI Reference

The `luxafor` CLI is built with [Typer](https://typer.tiangolo.com/) and provides two commands.

## `luxafor set-color`

Set the Luxafor Flag to a specific color.

```
Usage: luxafor set-color [OPTIONS] COLOR
```

### Arguments

| Argument | Type | Required | Description |
|---|---|---|---|
| `COLOR` | enum | Yes | Color to set the flag to |

### Available colors

`off`, `red`, `green`, `blue`, `cyan`, `magenta`, `yellow`, `white`

### Examples

```bash
luxafor set-color red
luxafor set-color off
luxafor set-color cyan
```

---

## `luxafor monitor`

Start the internet health monitor. Probes DNS resolvers continuously and drives the Luxafor Flag LED based on connectivity health.

```
Usage: luxafor monitor [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `--critical-after` / `-c` | int | 300 | Seconds of sustained downtime before the flag starts blinking red |

### Examples

```bash
# Default: blink red after 5 minutes of downtime
luxafor monitor

# Blink red after 1 minute of downtime
luxafor monitor --critical-after 60

# Short form
luxafor monitor -c 30
```

### Behavior

1. Connects to the Luxafor Flag via USB HID
2. Sets the flag to green (healthy)
3. Begins probing `8.8.8.8:53`, `1.1.1.1:53`, and `9.9.9.9:53` every 1.5 seconds
4. Updates LED color based on weighted health score
5. Runs until interrupted with `Ctrl+C`

### LED states

| Health | LED | Condition |
|---|---|---|
| 🟢 Green | Solid | Health score > 0.8 |
| 🟡 Yellow | Solid | Health score 0.4 – 0.8 |
| 🔴 Red | Solid | Health score ≤ 0.4 |
| 🔴 Red | Blinking | Down longer than `--critical-after` seconds |
| 🔵 Cyan | Flash | Anomalous packet loss (brief) |
