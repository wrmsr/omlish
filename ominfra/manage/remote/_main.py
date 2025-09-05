# ruff: noqa: UP006 UP007 UP045
import asyncio
import functools
import logging
import os
import signal
import threading
import time
import typing as ta

from omlish.asyncs.asyncio.streams import asyncio_open_stream_reader
from omlish.asyncs.asyncio.streams import asyncio_open_stream_writer
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.inject import Injector
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect
from omlish.logs.modules import get_module_logger
from omlish.os.deathsig import set_process_deathsig

from ...pyremote import pyremote_bootstrap_finalize
from ..bootstrap import MainBootstrap
from ..commands.local import LocalCommandExecutor
from .channel import RemoteChannel
from .channel import RemoteChannelImpl
from .execution import _RemoteCommandHandler
from .execution import _RemoteLogHandler


if ta.TYPE_CHECKING:
    from ..bootstrap_ import main_bootstrap
else:
    main_bootstrap: ta.Any = None


log = get_module_logger(globals())  # noqa


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
        return check.not_none(self.__bootstrap)

    @property
    def _injector(self) -> Injector:
        return check.not_none(self.__injector)

    #

    def _timebomb_main(
            self,
            delay_s: float,
            *,
            sig: int = signal.SIGINT,
            code: int = 1,
    ) -> None:
        time.sleep(delay_s)

        if (pgid := os.getpgid(0)) == os.getpid():
            os.killpg(pgid, sig)

        os._exit(code)  # noqa

    @cached_nullary
    def _timebomb_thread(self) -> ta.Optional[threading.Thread]:
        if (tbd := self._bootstrap.remote_config.timebomb_delay_s) is None:
            return None

        thr = threading.Thread(
            target=functools.partial(self._timebomb_main, tbd),
            name=f'{self.__class__.__name__}.timebomb',
            daemon=True,
        )

        thr.start()

        log.debug('Started timebomb thread: %r', thr)

        return thr

    #

    @cached_nullary
    def _log_handler(self) -> _RemoteLogHandler:
        return _RemoteLogHandler(self._chan)

    #

    async def _setup(self) -> None:
        check.none(self.__bootstrap)
        check.none(self.__injector)

        # Bootstrap

        self.__bootstrap = check.not_none(await self._chan.recv_obj(MainBootstrap))

        if (prd := self._bootstrap.remote_config.pycharm_remote_debug) is not None:
            pycharm_debug_connect(prd)

        self.__injector = main_bootstrap(self._bootstrap)

        self._chan.set_marshaler(self._injector[ObjMarshalerManager])

        # Post-bootstrap

        if self._bootstrap.remote_config.set_pgid:
            if os.getpgid(0) != os.getpid():
                log.debug('Setting pgid')
                os.setpgid(0, 0)

        if (ds := self._bootstrap.remote_config.deathsig) is not None:
            log.debug('Setting deathsig: %s', ds)
            set_process_deathsig(int(signal.Signals[f'SIG{ds.upper()}']))

        self._timebomb_thread()

        if self._bootstrap.remote_config.forward_logging:
            log.debug('Installing log forwarder')
            logging.root.addHandler(self._log_handler())

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
