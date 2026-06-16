from enum import Enum

import anyio
import httpx
from furl import furl

from ..util import setup_logger

logger = setup_logger()


class FlagColor(Enum):
    """
    Color values for the Luxafor Flag
    """

    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    WHITE = "white"
    CYAN = "cyan"
    MAGENTA = "magenta"


# {"token": self.token, "color": color.value}


class RemoteWebhookFlag:
    port: int
    token: str
    user_id: str

    def __init__(
        self,
        token: str = "CaUt1RwoiqSzeD9PuT-_tyUfR-9ZeTq31bF3kKAqbtY",
        user_id: str = "b72bbd0b799a",
        host: str = "localhost",
        port: int = 5383,
    ):
        """Initialize the Luxafor Flag device"""
        self.token = token
        self.user_id = user_id
        self.url = furl(scheme="http", host=host, port=port)

    async def solid_color(self, color: FlagColor):
        """Connect to the Luxafor Flag device"""
        async with httpx.AsyncClient() as client:
            url = str(self.url) + "/webhook/v1/actions/solid_color"
            json = {"userId": self.user_id, "actionFields": {"color": color.value}}
            await client.post(url, json=json, timeout=10)

    def set_color(self, color: FlagColor):
        """
        Set the color of the Luxafor Flag
        """
        # buffer = HIDBuffer(report_id=0x00, color=color)

        if not self.device:
            self.connect()

        if self.device:
            try:
                self.device.write(bytes(buffer))
            except Exception as e:
                logger.error(
                    f"Error setting color: {e}",
                    exception=e,
                    color=color,
                    buffer=buffer,
                )
                self.device = None
            else:
                logger.info("Color set", color=color, buffer=buffer)


async def main():
    flag = RemoteWebhookFlag()
    await flag.solid_color(FlagColor.RED)


if __name__ == "__main__":
    anyio.run(main)
