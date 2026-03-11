from omdev.tui import textual as tx
from omlish import check
from omlish.term.alt import render_write_from_alt

from .types import ChatAppGetter


##


class BackgroundTerminalRenderer:
    def __init__(self, app: ChatAppGetter) -> None:
        super().__init__()

        self._app = app

    async def background_render_widget(
            self,
            widget: tx.Widget,
            *,
            no_refresh: bool = False,
    ) -> None:
        app = await self._app()

        ansi = tx.render_full_widget_ansi(widget, app.console, strip=True, reset=True)

        pwd = check.isinstance(app._driver, tx.PendingWritesDriverMixin)  # noqa
        pwd.queue_primary_buffer_write(render_write_from_alt(ansi, '\n\n'))

        if not no_refresh:
            app.refresh(layout=True)
