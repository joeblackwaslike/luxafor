from enum import StrEnum
from typing import Annotated

import anyio
import typer

from luxafor.local import FlagColor, LuxaforFlag
from luxafor.monitor import start_monitor

app = typer.Typer()


class Color(StrEnum):
    """CLI-friendly color names mapped to FlagColor."""

    OFF = "off"
    BLUE = "blue"
    CYAN = "cyan"
    GREEN = "green"
    MAGENTA = "magenta"
    RED = "red"
    WHITE = "white"
    YELLOW = "yellow"


COLOR_MAP: dict[Color, FlagColor] = {
    Color.OFF: FlagColor.OFF,
    Color.BLUE: FlagColor.BLUE,
    Color.CYAN: FlagColor.CYAN,
    Color.GREEN: FlagColor.GREEN,
    Color.MAGENTA: FlagColor.MAGENTA,
    Color.RED: FlagColor.RED,
    Color.WHITE: FlagColor.WHITE,
    Color.YELLOW: FlagColor.YELLOW,
}


@app.command()
def set_color(
    color: Annotated[Color, typer.Argument(help="Color to set the flag to.")],
) -> None:
    """Set the Luxafor Flag to the given color."""
    flag = LuxaforFlag()
    flag.set_color(COLOR_MAP[color])


@app.command()
def monitor(
    critical_after: Annotated[
        int,
        typer.Option("--critical-after", "-c", help="Seconds of outage before blinking red."),
    ] = 300,
) -> None:
    """Monitor internet health and display status on the Luxafor Flag."""
    anyio.run(start_monitor, critical_after)


if __name__ == "__main__":
    app()
