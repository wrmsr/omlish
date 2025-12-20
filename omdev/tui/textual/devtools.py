# ruff: noqa: UP037 UP045
import inspect
import logging
import typing as ta

import textual.constants

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .logging2 import translate_log_level


with lang.auto_proxy_import(globals()):
    from textual_dev import client as tx_dev_client
    from textual_dev import redirect_output as tx_dev_redirect_output


##


@dc.dataclass(frozen=True, kw_only=True)
class DevtoolsConfig:
    host: str = '127.0.0.1'

    # https://github.com/Textualize/textual/blob/676045381b7178c3bc94b86901f20764e08aca49/src/textual/constants.py#L125
    port: int = 8081

    @classmethod
    def from_env(cls) -> 'DevtoolsConfig':
        return cls(
            host=textual.constants.DEVTOOLS_HOST,
            port=textual.constants.DEVTOOLS_PORT,
        )


async def connect_devtools(config: DevtoolsConfig) -> ta.Optional['tx_dev_client.DevtoolsClient']:
    try:
        from textual_dev.client import DevtoolsClient  # noqa
    except ImportError:
        # Dev dependencies not installed
        return None

    devtools = DevtoolsClient(
        config.host,
        config.port,
    )

    from textual_dev.client import DevtoolsConnectionError

    try:
        await devtools.connect()
    except DevtoolsConnectionError as e:  # noqa
        return None

    return devtools


##


class DevtoolsAppMixin:
    _skip_devtools_management: bool = False

    def _install_devtools(self, devtools: 'tx_dev_client.DevtoolsClient') -> None:
        check.none(getattr(self, 'devtools', None))
        check.none(getattr(self, '_devtools_redirector', None))

        # https://github.com/Textualize/textual/blob/676045381b7178c3bc94b86901f20764e08aca49/src/textual/app.py#L730-L741
        setattr(self, 'devtools', devtools)
        setattr(self, '_devtools_redirector', tx_dev_redirect_output.StdoutRedirector(devtools))

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


class DevtoolsSetup(lang.Func1[DevtoolsAppMixin, None]):
    pass


class DevtoolsManager:
    def __init__(
            self,
            config: DevtoolsConfig = DevtoolsConfig(),
    ) -> None:
        super().__init__()

        self._config = config
        self._devtools: ta.Optional['tx_dev_client.DevtoolsClient'] = None
        self._setup: DevtoolsSetup | None = None

    async def get_setup(self) -> DevtoolsSetup:
        if self._setup is None:
            check.none(self._devtools)

            self._devtools = await connect_devtools(self._config)

            self._setup = DevtoolsSetup(self._setup_app_dev_tools)

        return self._setup

    def _setup_app_dev_tools(self, app: DevtoolsAppMixin) -> None:
        if (devtools := self._devtools) is None:
            return

        check.isinstance(app, DevtoolsAppMixin)._install_devtools(devtools)  # noqa

    async def aclose(self) -> None:
        if (devtools := self._devtools) is not None and devtools.is_connected:
            await devtools.disconnect()


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


def set_root_logger_to_devtools(devtools: ta.Optional['tx_dev_client.DevtoolsClient']) -> None:
    from omlish.logs.std.standard import _locking_logging_module_lock  # noqa
    from omlish.logs.std.standard import StandardConfiguredLoggingHandler

    with _locking_logging_module_lock():
        std_handler = next((h for h in logging.root.handlers if isinstance(h, StandardConfiguredLoggingHandler)), None)

        dt_handler = DevtoolsLoggingHandler(devtools, std_handler)

        logging.root.handlers = [dt_handler]
