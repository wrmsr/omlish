# ruff: noqa: UP006 UP007
import abc
import asyncio
import contextlib
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.marshal import ObjMarshalerManager

from ...pyremote import PyremoteBootstrapDriver
from ...pyremote import PyremoteBootstrapOptions
from ...pyremote import pyremote_build_bootstrap_cmd
from ..bootstrap import MainBootstrap
from ._main import _remote_execution_main  # noqa
from .channel import RemoteChannelImpl
from .execution import RemoteCommandExecutor
from .payload import RemoteExecutionPayloadFile
from .payload import get_remote_payload_src
from .spawning import RemoteSpawning


##


class RemoteExecutionConnector(abc.ABC):
    @abc.abstractmethod
    def connect(
            self,
            tgt: RemoteSpawning.Target,
            bs: MainBootstrap,
    ) -> ta.AsyncContextManager[RemoteCommandExecutor]:
        raise NotImplementedError


##


class PyremoteRemoteExecutionConnector(RemoteExecutionConnector):
    def __init__(
            self,
            *,
            spawning: RemoteSpawning,
            msh: ObjMarshalerManager,
            payload_file: ta.Optional[RemoteExecutionPayloadFile] = None,
    ) -> None:
        super().__init__()

        self._spawning = spawning
        self._msh = msh
        self._payload_file = payload_file

    #

    @cached_nullary
    def _payload_src(self) -> str:
        return get_remote_payload_src(file=self._payload_file)

    @cached_nullary
    def _remote_src(self) -> ta.Sequence[str]:
        return [
            self._payload_src(),
            '_remote_execution_main()',
        ]

    @cached_nullary
    def _spawn_src(self) -> str:
        return pyremote_build_bootstrap_cmd(__package__ or 'manage')

    #

    @contextlib.asynccontextmanager
    async def connect(
            self,
            tgt: RemoteSpawning.Target,
            bs: MainBootstrap,
    ) -> ta.AsyncGenerator[RemoteCommandExecutor, None]:
        spawn_src = self._spawn_src()
        remote_src = self._remote_src()

        async with self._spawning.spawn(
                tgt,
                spawn_src,
                debug=bs.main_config.debug,
        ) as proc:
            res = await PyremoteBootstrapDriver(  # noqa
                remote_src,
                PyremoteBootstrapOptions(
                    debug=bs.main_config.debug,
                ),
            ).async_run(
                proc.stdout,
                proc.stdin,
            )

            chan = RemoteChannelImpl(
                proc.stdout,
                proc.stdin,
                msh=self._msh,
            )

            await chan.send_obj(bs)

            rce: RemoteCommandExecutor
            async with contextlib.aclosing(RemoteCommandExecutor(chan)) as rce:
                await rce.start()

                yield rce


##


class AsyncioBytesChannelTransport(asyncio.Transport):
    def __init__(self, reader) -> None:
        super().__init__()

        self.reader = reader
        self.closed = asyncio.Future()

    def write(self, data):
        self.reader.feed_data(data)

    def close(self):
        self.reader.feed_eof()
        if not self.closed.done():
            self.closed.set_result(True)

    def is_closing(self):
        return self.closed.done()


def asyncio_create_bytes_channel(
        loop: ta.Any = None,
) -> ta.Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    if loop is None:
        loop = asyncio.get_running_loop()

    reader = asyncio.StreamReader()

    protocol = asyncio.StreamReaderProtocol(reader)
    transport = AsyncioBytesChannelTransport(reader)
    writer = asyncio.StreamWriter(transport, protocol, reader, loop)

    return reader, writer


class InProcessRemoteExecutionConnector(RemoteExecutionConnector):
    def __init__(
            self,
            *,
            msh: ObjMarshalerManager,
    ) -> None:
        super().__init__()

        self._msh = msh

    @contextlib.asynccontextmanager
    async def connect(
            self,
            tgt: RemoteSpawning.Target,
            bs: MainBootstrap,
    ) -> ta.AsyncGenerator[RemoteCommandExecutor, None]:
        r0, w0 = asyncio_create_bytes_channel()
        r1, w1 = asyncio_create_bytes_channel()

        chan = RemoteChannelImpl(
            proc.stdout,
            proc.stdin,
            msh=self._msh,
        )

        await chan.send_obj(bs)

        rce: RemoteCommandExecutor
        async with contextlib.aclosing(RemoteCommandExecutor(chan)) as rce:
            await rce.start()

            yield rce
