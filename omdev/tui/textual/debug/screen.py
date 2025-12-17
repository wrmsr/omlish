from textual.geometry import Region
from textual.screen import Screen
from textual.widget import Widget


##


def get_screen_zbuffer(screen: Screen) -> list[list[list[tuple[Widget, Region]] | None]]:
    width, height = screen.size

    zbuffer: list[list[list[tuple[Widget, Region]] | None]] = [
        [None for _ in range(width)]
        for _ in range(height)
    ]

    for y in range(height):
        for x in range(width):
            try:
                zbuffer[y][x] = list(screen.get_widgets_at(x, y))
            except Exception:  # noqa
                pass

    return zbuffer
