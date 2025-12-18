import logging

from ..base import ChatInterface
from .app import ChatApp


##


class _HackLoggingHandler(logging.Handler):
    def emit(self, record):
        pass


def _hack_loggers() -> None:
    from omlish.logs.standard import _locking_logging_module_lock  # noqa
    from omlish.logs.standard import StandardConfiguredLoggingHandler

    with _locking_logging_module_lock():
        std_handler = next((h for h in logging.root.handlers if isinstance(h, StandardConfiguredLoggingHandler)), None)

        hack_handler = _HackLoggingHandler()

        if std_handler is not None:
            hack_handler.setFormatter(std_handler.formatter)

            for std_filter in std_handler.filters:
                hack_handler.addFilter(std_filter)

        logging.root.handlers = [hack_handler]


##


class TextualChatInterface(ChatInterface):
    def __init__(
            self,
            *,
            app: ChatApp,
    ) -> None:
        super().__init__()

        self._app = app

    async def run(self) -> None:
        _hack_loggers()

        await self._app.run_async()
