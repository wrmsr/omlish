import inspect
import logging
import typing as ta

from omdev.tui import textual as tx

from ..base import ChatInterface
from .app import ChatApp


if ta.TYPE_CHECKING:
    from textual_dev.client import DevtoolsClient


##


def _translate_log_level(level: int) -> tuple['tx.LogGroup', 'tx.LogVerbosity']:
    if level >= logging.ERROR:
        return (tx.LogGroup.ERROR, tx.LogVerbosity.HIGH)
    elif level >= logging.WARNING:
        return (tx.LogGroup.ERROR, tx.LogVerbosity.HIGH)
    elif level >= logging.INFO:
        return (tx.LogGroup.INFO, tx.LogVerbosity.NORMAL)
    elif level >= logging.DEBUG:
        return (tx.LogGroup.DEBUG, tx.LogVerbosity.NORMAL)
    else:
        return (tx.LogGroup.UNDEFINED, tx.LogVerbosity.NORMAL)


class _HackLoggingHandler(logging.Handler):
    """
    TODO:
     - reify caller from LogContextInfos
     - queue worker, this blocks the asyncio thread lol
     - move to omdev.tui.textual obviously
    """

    def __init__(self, devtools: ta.Optional['DevtoolsClient']) -> None:
        super().__init__()

        self._devtools = devtools

    def emit(self, record: logging.LogRecord) -> None:
        if (devtools := self._devtools) is not None and devtools.is_connected:
            from textual_dev.client import DevtoolsLog

            msg = self.format(record)

            caller = inspect.Traceback(
                filename=record.filename,
                lineno=record.lineno,
                function=record.funcName,
                code_context=None,
                index=None,
            )

            group, verbosity = _translate_log_level(record.levelno)

            devtools.log(
                DevtoolsLog(
                    msg,
                    caller=caller,
                ),
                group=group,
                verbosity=verbosity,
            )


def _hack_loggers(devtools: ta.Optional['DevtoolsClient']) -> None:
    from omlish.logs.std.standard import _locking_logging_module_lock  # noqa
    from omlish.logs.std.standard import StandardConfiguredLoggingHandler

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
