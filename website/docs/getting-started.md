---
sidebar_position: 3
title: Getting Started
---

# Getting Started

This guide walks you through plugging in your Luxafor Flag and running your first commands.

## 1. Plug in the device

Connect the Luxafor Flag to a USB port. The device should appear as an HID device with vendor ID `0x04D8` and product ID `0xF372`.

## 2. Set a color

```bash
luxafor set-color green
```

The flag should light up green. Available colors: `off`, `red`, `green`, `blue`, `cyan`, `magenta`, `yellow`, `white`.

If you see a connection error, check that the device is plugged in and you have [USB permissions](./installation#usb-permissions).

## 3. Start the internet monitor

```bash
luxafor monitor
```

The flag turns green immediately, then begins probing DNS resolvers every 1.5 seconds. If your internet connection degrades or drops, the LED color changes to reflect the current health status:

| Status | LED | Meaning |
|---|---|---|
| Healthy | 🟢 Green | All probes succeeding |
| Degraded | 🟡 Yellow | Some packet loss |
| Down | 🔴 Red | Most or all probes failing |
| Critical | 🔴 Blinking red | Down longer than the critical threshold |

Press `Ctrl+C` to stop the monitor.

## 4. Customize the critical threshold

By default, the flag starts blinking red after 5 minutes (300 seconds) of continuous downtime. Shorten it for faster alerts:

```bash
luxafor monitor --critical-after 60
```

## 5. Run as a background service

For persistent monitoring, set up a macOS LaunchAgent:

```bash
cat > ~/Library/LaunchAgents/com.luxafor.monitor.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.luxafor.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/your/venv/bin/luxafor</string>
        <string>monitor</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.luxafor.monitor.plist
```

Replace `/path/to/your/venv/bin/luxafor` with the actual path from `which luxafor` inside your virtual environment.

## Next steps

- [CLI Reference](./cli-reference) — all commands and options
- [Monitor Guide](./guides/monitor) — health scoring, hysteresis, anomaly detection
- [HID Protocol](./guides/hid-protocol) — low-level USB communication
