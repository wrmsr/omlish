import html
import typing as ta


def escape(s: str) -> str:
    return html.escape(s).replace('@', '&#64;')


class Color(ta.NamedTuple):
    r: int
    g: int
    b: int


def gen_rainbow(steps: int) -> list[Color]:
    colors = []
    for r in range(steps):
        colors.append(Color(r * 255 // steps, 255, 0))
    for g in range(steps, 0, -1):
        colors.append(Color(255, g * 255 // steps, 0))
    for b in range(steps):
        colors.append(Color(255, 0, b * 255 // steps))
    for r in range(steps, 0, -1):
        colors.append(Color(r * 255 // steps, 0, 255))
    for g in range(steps):
        colors.append(Color(0, g * 255 // steps, 255))
    for b in range(steps, 0, -1):
        colors.append(Color(0, 255, b * 255 // steps))
    colors.append(Color(0, 255, 0))
    return colors
