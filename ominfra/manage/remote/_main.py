# ruff: noqa: UP006 UP007
import asyncio
import logging
import typing as ta

from omlish.lite.asyncio.asyncio import asyncio_open_stream_reader
from omlish.lite.asyncio.asyncio import asyncio_open_stream_writer
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_none
from omlish.lite.check import check_not_none
from omlish.lite.inject import Injector
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect

from ...pyremote import pyremote_bootstrap_finalize
from ..bootstrap import MainBootstrap
from ..commands.execution import LocalCommandExecutor
from .channel import RemoteChannel
from .channel import RemoteChannelImpl
from .execution import _RemoteCommandHandler
from .execution import _RemoteLogHandler


if ta.TYPE_CHECKING:
    from ..bootstrap_ import main_bootstrap
else:
    main_bootstrap: ta.Any = None


##


class _RemoteExecutionLogHandler(logging.Handler):
    def __init__(self, fn: ta.Callable[[str], None]) -> None:
        super().__init__()
        self._fn = fn

    def emit(self, record):
        msg = self.format(record)
        self._fn(msg)


##


class _RemoteExecutionMain:
    def __init__(
            self,
            chan: RemoteChannel,
    ) -> None:
        super().__init__()

        self._chan = chan

        self.__bootstrap: ta.Optional[MainBootstrap] = None
        self.__injector: ta.Optional[Injector] = None

    @property
    def _bootstrap(self) -> MainBootstrap:
        return check_not_none(self.__bootstrap)

    @property
    def _injector(self) -> Injector:
        return check_not_none(self.__injector)

    #

    @cached_nullary
    def _log_handler(self) -> _RemoteLogHandler:
        return _RemoteLogHandler(self._chan)

    #

    async def _setup(self) -> None:
        check_none(self.__bootstrap)
        check_none(self.__injector)

        # Bootstrap

        self.__bootstrap = check_not_none(await self._chan.recv_obj(MainBootstrap))

        if (prd := self._bootstrap.remote_config.pycharm_remote_debug) is not None:
            pycharm_debug_connect(prd)

        if self._bootstrap.remote_config.forward_logging:
            logging.root.addHandler(self._log_handler())

        # Injector

        self.__injector = main_bootstrap(self._bootstrap)

        self._chan.set_marshaler(self._injector[ObjMarshalerManager])

    #

    async def run(self) -> None:
        await self._setup()

        executor = self._injector[LocalCommandExecutor]

        handler = _RemoteCommandHandler(self._chan, executor)

        await handler.run()


def _remote_execution_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    async def inner() -> None:
        input = await asyncio_open_stream_reader(rt.input)  # noqa
        output = await asyncio_open_stream_writer(rt.output)

        chan = RemoteChannelImpl(
            input,
            output,
        )

        await _RemoteExecutionMain(chan).run()

    asyncio.run(inner())
