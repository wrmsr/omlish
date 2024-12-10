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
from omlish.lite.logs import log
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect

from ...pyremote import pyremote_bootstrap_finalize
from ..bootstrap import MainBootstrap
from ..commands.base import CommandOutputOrExceptionData
from ..commands.execution import LocalCommandExecutor
from .channel import RemoteChannel


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
    def _log_handler(self) -> _RemoteExecutionLogHandler:
        def log_fn(s: str) -> None:
            async def inner():
                await _RemoteExecutionProtocol.LogResponse(s).send(self._chan)

            loop = asyncio.get_running_loop()
            if loop is not None:
                asyncio.run_coroutine_threadsafe(inner(), loop)

        return _RemoteExecutionLogHandler(log_fn)

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

        ce = self._injector[LocalCommandExecutor]

        cmd_futs_by_seq: ta.Dict[int, asyncio.Future] = {}

        async def handle_cmd(req: _RemoteExecutionProtocol.CommandRequest) -> None:
            res = await ce.try_execute(
                req.cmd,
                log=log,
                omit_exc_object=True,
            )

            await _RemoteExecutionProtocol.CommandResponse(
                seq=req.seq,
                res=CommandOutputOrExceptionData(
                    output=res.output,
                    exception=res.exception,
                ),
            ).send(self._chan)

            cmd_futs_by_seq.pop(req.seq)  # noqa

        while True:
            req = await _RemoteExecutionProtocol.Request.recv(self._chan)
            if req is None:
                break

            if isinstance(req, _RemoteExecutionProtocol.CommandRequest):
                fut = asyncio.create_task(handle_cmd(req))
                cmd_futs_by_seq[req.seq] = fut

            else:
                raise TypeError(req)


def _remote_execution_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    async def inner() -> None:
        input = await asyncio_open_stream_reader(rt.input)  # noqa
        output = await asyncio_open_stream_writer(rt.output)

        chan = RemoteChannel(
            input,
            output,
        )

        await _RemoteExecutionMain(chan).run()

    asyncio.run(inner())
