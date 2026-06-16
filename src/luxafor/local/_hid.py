from enum import Enum

import hid

from ..util import setup_logger

logger = setup_logger()


class FlagColor(Enum):
    """
    Color values for the Luxafor Flag
    """

    OFF = 0x4F
    BLUE = 0x42
    CYAN = 0x43
    GREEN = 0x47
    MAGENTA = 0x4D
    RED = 0x52
    WHITE = 0x57
    YELLOW = 0x59


class HIDBuffer:
    def __init__(self, report_id: int = 0x00, color: FlagColor = FlagColor.OFF):
        self.buffer = [0x00] * 8
        self.buffer[0] = report_id
        self.buffer[2] = color.value

    def __repr__(self):
        return f"{type(self).__name__}{bytes(self.buffer)}"

    def __bytes__(self):
        return bytes(self.buffer)

    def __len__(self):
        return len(self.buffer)

    def __getitem__(self, index: int):
        return self.buffer[index]

    def __setitem__(self, index: int, value: int):
        self.buffer[index] = value

    def __iter__(self):
        return iter(self.buffer)

    def __contains__(self, item: int):
        return item in self.buffer


class LuxaforFlag:
    VENDOR_ID: int = 0x04D8
    PRODUCT_ID: int = 0xF372

    device: hid.Device | None

    def __init__(self):
        """Initialize the Luxafor Flag device"""
        self.device = None
        self.connect()

    def connect(self):
        """Connect to the Luxafor Flag device"""
        try:
            self.device = hid.Device(self.VENDOR_ID, self.PRODUCT_ID)
        except Exception as e:
            logger.error(f"Error connecting to Luxafor Flag: {e}", extra={"exception": e})
            self.device = None
        else:
            logger.info("Luxafor Flag initialized", flag=self)

    def set_color(self, color: FlagColor):
        """
        Set the color of the Luxafor Flag
        """
        buffer = HIDBuffer(report_id=0x00, color=color)

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


if __name__ == "__main__":
    flag = LuxaforFlag()
    flag.set_color(FlagColor.RED)
