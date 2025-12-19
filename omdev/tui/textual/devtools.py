import inspect
import logging
import typing as ta

from textual.app import App

from omlish import check
from omlish import lang

from .logging2 import translate_log_level


with lang.auto_proxy_import(globals()):
    from textual_dev import client as tx_dev_client


##


def setup_app_devtools(
        app: App,
        host: str = '127.0.0.1',
        port: int | None = None,
) -> bool:
    if app.devtools is not None:
        return False

    check.none(app._devtools_redirector)  # noqa

    try:
        from textual_dev.client import DevtoolsClient  # noqa
        from textual_dev.redirect_output import StdoutRedirector  # noqa
    except ImportError:
        # Dev dependencies not installed
        return False

    app.devtools = DevtoolsClient(
        host,
        port,
    )

    app._devtools_redirector = StdoutRedirector(app.devtools)  # noqa

    return True


##


class DevtoolsLoggingHandler(logging.Handler):
    """
    TODO:
     - reify caller from LogContextInfos
     - queue worker, this blocks the asyncio thread lol
    """

    def __init__(
            self,
            devtools: ta.Optional['tx_dev_client.DevtoolsClient'],
            prototype_handler: logging.Handler | None = None,
    ) -> None:
        super().__init__()

        self._devtools = devtools

        if prototype_handler is not None:
            self.setFormatter(prototype_handler.formatter)
            for lf in prototype_handler.filters:
                self.addFilter(lf)

    def emit(self, record: logging.LogRecord) -> None:
        if (devtools := self._devtools) is None or not devtools.is_connected:
            return

        msg = self.format(record)

        caller = inspect.Traceback(
            filename=record.filename,
            lineno=record.lineno,
            function=record.funcName,
            code_context=None,
            index=None,
        )

        group, verbosity = translate_log_level(record.levelno)

        devtools.log(
            tx_dev_client.DevtoolsLog(
                msg,
                caller=caller,
            ),
            group=group,
            verbosity=verbosity,
        )
