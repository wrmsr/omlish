# ruff: noqa: UP006 UP007
import asyncio
import contextlib
import typing as ta

from omlish.asyncs.asyncio.channels import asyncio_create_bytes_channel
from omlish.lite.cached import cached_nullary
from omlish.lite.contextmanagers import aclosing
from omlish.lite.marshal import ObjMarshalerManager

from ...pyremote import PyremoteBootstrapDriver
from ...pyremote import PyremoteBootstrapOptions
from ...pyremote import pyremote_build_bootstrap_cmd
from ..bootstrap import MainBootstrap
from ..commands.local import LocalCommandExecutor
from ._main import _remote_execution_main  # noqa
from .channel import RemoteChannelImpl
from .execution import RemoteCommandExecutor
from .execution import _RemoteCommandHandler
from .payload import RemoteExecutionPayloadFile
from .payload import get_remote_payload_src
from .spawning import RemoteSpawning


##


class PyremoteRemoteExecutionConnector:
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
            async with aclosing(RemoteCommandExecutor(chan)) as rce:
                await rce.start()

                yield rce


##


class InProcessRemoteExecutionConnector:
    def __init__(
            self,
            *,
            msh: ObjMarshalerManager,
            local_executor: LocalCommandExecutor,
    ) -> None:
        super().__init__()

        self._msh = msh
        self._local_executor = local_executor

    @contextlib.asynccontextmanager
    async def connect(self) -> ta.AsyncGenerator[RemoteCommandExecutor, None]:
        r0, w0 = asyncio_create_bytes_channel()
        r1, w1 = asyncio_create_bytes_channel()

        remote_chan = RemoteChannelImpl(r0, w1, msh=self._msh)
        local_chan = RemoteChannelImpl(r1, w0, msh=self._msh)

        rch = _RemoteCommandHandler(
            remote_chan,
            self._local_executor,
        )
        rch_task = asyncio.create_task(rch.run())  # noqa
        try:
            rce: RemoteCommandExecutor
            async with aclosing(RemoteCommandExecutor(local_chan)) as rce:
                await rce.start()

                yield rce

        finally:
            rch.stop()
            await rch_task
