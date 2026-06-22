---
sidebar_position: 3
title: Webhook Client
---

# Webhook Client

The `luxafor.remote` subpackage provides an async HTTP client for the Luxafor webhook API. This allows controlling Luxafor devices remotely over HTTP instead of direct USB.

## Usage

```python
import anyio
from luxafor.remote import RemoteWebhookFlag, FlagColor

async def main():
    flag = RemoteWebhookFlag(
        token="your-webhook-token",
        user_id="your-user-id",
        host="localhost",
        port=5383,
    )
    await flag.solid_color(FlagColor.RED)

anyio.run(main)
```

## RemoteWebhookFlag

### Constructor

```python
RemoteWebhookFlag(
    token: str = "...",
    user_id: str = "...",
    host: str = "localhost",
    port: int = 5383,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `token` | str | (placeholder) | Webhook authentication token |
| `user_id` | str | (placeholder) | Luxafor user ID |
| `host` | str | `"localhost"` | Webhook server hostname |
| `port` | int | `5383` | Webhook server port |

The constructor builds the base URL using [furl](https://pypi.org/project/furl/): `http://{host}:{port}`.

### `solid_color(color: FlagColor)`

Sets the device to a solid color via HTTP POST.

```python
await flag.solid_color(FlagColor.GREEN)
```

**Endpoint:** `POST /webhook/v1/actions/solid_color`

**Payload:**
```json
{
  "userId": "your-user-id",
  "actionFields": {
    "color": "green"
  }
}
```

**Timeout:** 10 seconds

Uses `httpx.AsyncClient` for the HTTP request.

## FlagColor (remote)

The remote `FlagColor` enum uses string values (unlike the local HID version which uses hex codes):

| Color | Value |
|---|---|
| RED | `"red"` |
| GREEN | `"green"` |
| YELLOW | `"yellow"` |
| BLUE | `"blue"` |
| WHITE | `"white"` |
| CYAN | `"cyan"` |
| MAGENTA | `"magenta"` |

:::note
The remote and local `FlagColor` enums are separate classes with different value types. Import from the correct subpackage:
- `from luxafor.local import FlagColor` — hex values for USB HID
- `from luxafor.remote import FlagColor` — string values for webhooks
:::
