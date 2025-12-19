import inspect
import logging
import typing as ta

from omlish import check
from omlish import lang

from .logging2 import translate_log_level


with lang.auto_proxy_import(globals()):
    from textual_dev import client as tx_dev_client


##


class DevtoolsAppMixin:
    devtools: ta.Optional['tx_dev_client.DevtoolsClient'] = None

    _skip_devtools_management: bool = False

    def _install_devtools(self, devtools: 'tx_dev_client.DevtoolsClient') -> None:
        check.none(self.devtools)
        check.none(self._devtools_redirector)  # type: ignore

        # https://github.com/Textualize/textual/blob/676045381b7178c3bc94b86901f20764e08aca49/src/textual/app.py#L730-L741
        self.devtools = devtools
        self._devtools_redirector = StdoutRedirector(self.devtools)  # type: ignore

        self._skip_devtools_management = True

    async def _init_devtools(self) -> None:
        if self._skip_devtools_management:
            return

        await super()._init_devtools()  # type: ignore  # noqa

    async def _disconnect_devtools(self) -> None:
        if self._skip_devtools_management:
            return

        await super()._disconnect_devtools()  # type: ignore  # noqa


##


async def connect_devtools(
        host: str = '127.0.0.1',
        port: int | None = None,
) -> ta.Optional['tx_dev_client.DevtoolsClient']:
    try:
        from textual_dev.client import DevtoolsClient  # noqa
    except ImportError:
        # Dev dependencies not installed
        return None

    devtools = DevtoolsClient(
        host,
        port,
    )

    from textual_dev.client import DevtoolsConnectionError

    try:
        await devtools.connect()
    except DevtoolsConnectionError as e:  # noqa
        return None

    return devtools


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
