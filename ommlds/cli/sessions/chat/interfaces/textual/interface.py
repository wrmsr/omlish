import inspect
import logging
import typing as ta

from ..base import ChatInterface
from .app import ChatApp


if ta.TYPE_CHECKING:
    from textual_dev.client import DevtoolsClient


##


class _HackLoggingHandler(logging.Handler):
    """
    TODO:
     - reify caller from LogContextInfos
     - queue worker
     - translate verbosity and group
    """

    def __init__(self, devtools: ta.Optional['DevtoolsClient']) -> None:
        super().__init__()

        self._devtools = devtools

    def emit(self, record):
        if (devtools := self._devtools) is not None and devtools.is_connected:
            from textual_dev.client import DevtoolsLog

            caller = inspect.Traceback(
                filename='',
                lineno=0,
                function='',
                code_context=None,
                index=None,
            )

            devtools.log(
                DevtoolsLog(
                    repr(record),
                    caller=caller,
                ),
            )


def _hack_loggers(devtools: ta.Optional['DevtoolsClient']) -> None:
    from omlish.logs.standard import _locking_logging_module_lock  # noqa
    from omlish.logs.standard import StandardConfiguredLoggingHandler

    with _locking_logging_module_lock():
        std_handler = next((h for h in logging.root.handlers if isinstance(h, StandardConfiguredLoggingHandler)), None)

        hack_handler = _HackLoggingHandler(devtools)

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
        _hack_loggers(self._app.devtools)

        await self._app.run_async()
