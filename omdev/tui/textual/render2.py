import io

from rich.console import Console
from textual._compositor import Compositor  # noqa
from textual.geometry import Size
from textual.widget import Widget


##


def render_full_widget_ansi(
        widget: Widget,
        console: Console,
        size: Size | None = None,
        *,
        strip: bool = False,
        reset: bool = False,
) -> str:
    if size is None:
        size = Size(widget.size.width, widget.size.height)

    comp = Compositor()
    comp.reflow(widget, size)

    update = comp.render_full_update(simplify=True)

    out = io.StringIO()
    for row in update.strips:
        line = ''.join(strip.render(console) for strip in row)
        if strip:
            line = line.rstrip(' ')
        out.write(line)
        if reset:
            out.write('\x1b[0m')
        out.write('\n')
    ansi = out.getvalue()

    return ansi
