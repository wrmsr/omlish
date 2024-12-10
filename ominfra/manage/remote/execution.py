# ruff: noqa: UP006 UP007
import abc
import asyncio
import contextlib
import dataclasses as dc
import itertools
import logging
import typing as ta

from omlish.lite.asyncio.asyncio import asyncio_open_stream_reader
from omlish.lite.asyncio.asyncio import asyncio_open_stream_writer
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_isinstance
from omlish.lite.check import check_none
from omlish.lite.check import check_not_none
from omlish.lite.check import check_state
from omlish.lite.inject import Injector
from omlish.lite.logs import log
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect

from ...pyremote import pyremote_bootstrap_finalize
from ..bootstrap import MainBootstrap
from ..commands.base import Command
from ..commands.base import CommandException
from ..commands.base import CommandExecutor
from ..commands.base import CommandOutputOrException
from ..commands.base import CommandOutputOrExceptionData
from ..commands.execution import LocalCommandExecutor
from .channel import RemoteChannel


if ta.TYPE_CHECKING:
    from ..bootstrap_ import main_bootstrap
else:
    main_bootstrap: ta.Any = None


T = ta.TypeVar('T')


##


class _RemoteExecutionProtocol:
    class Message(abc.ABC):
        _message_cls: ta.ClassVar[ta.Type['_RemoteExecutionProtocol.Message']]

        async def send(self, chan: RemoteChannel) -> None:
            await chan.send_obj(self, self._message_cls)

        @classmethod
        async def recv(cls: ta.Type[T], chan: RemoteChannel) -> ta.Optional[T]:
            return await chan.recv_obj(cls._message_cls)  # type: ignore

    #

    class Request(Message, abc.ABC):  # noqa
        pass

    Request._message_cls = Request  # noqa

    @dc.dataclass(frozen=True)
    class CommandRequest(Request):
        seq: int
        cmd: Command

    #

    class Response(Message, abc.ABC):  # noqa
        pass

    Response._message_cls = Response  # noqa

    @dc.dataclass(frozen=True)
    class LogResponse(Response):
        s: str

    @dc.dataclass(frozen=True)
    class CommandResponse(Response):
        seq: int
        res: CommandOutputOrExceptionData


##


class _RemoteCommandHandler:
    def __init__(
            self,
            chan: RemoteChannel,
            executor: CommandExecutor,
            *,
            stop: ta.Optional[asyncio.Event] = None,
    ) -> None:
        super().__init__()

        self._chan = chan
        self._executor = executor
        self._stop = stop if stop is not None else asyncio.Event()

        self._cmd_futs_by_seq: ta.Dict[int, asyncio.Future] = {}

    async def _handle_command_request(self, req: _RemoteExecutionProtocol.CommandRequest) -> None:
        res = await self._executor.try_execute(
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

    async def _handle_request(self, req: _RemoteExecutionProtocol.CommandRequest) -> None:
        if isinstance(req, _RemoteExecutionProtocol.CommandRequest):
            fut = asyncio.create_task(self._handle_command_request(req))
            self._cmd_futs_by_seq[req.seq] = fut

        else:
            raise TypeError(req)

    async def run(self) -> None:
        stop_task = asyncio.create_task(self._stop.wait())
        recv_task: ta.Optional[asyncio.Task] = None

        while not self._stop.is_set():
            if recv_task is None:
                recv_task = asyncio.create_task(_RemoteExecutionProtocol.Response.recv(self._chan))

            done, pending = await asyncio.wait([
                stop_task,
                recv_task,
            ], return_when=asyncio.FIRST_COMPLETED)

            if recv_task in done:
                req = check_isinstance(recv_task.result(), (_RemoteExecutionProtocol.Request, type(None)))
                recv_task = None

                if req is None:
                    break

                await self._handle_request(req)


##


@dc.dataclass()
class RemoteCommandError(Exception):
    e: CommandException


class RemoteCommandExecutor(CommandExecutor):
    def __init__(self, chan: RemoteChannel) -> None:
        super().__init__()

        self._chan = chan

        self._cmd_seq = itertools.count()
        self._queue: asyncio.Queue = asyncio.Queue()  # asyncio.Queue[RemoteCommandExecutor._Request]
        self._stop = asyncio.Event()
        self._loop_task: ta.Optional[asyncio.Task] = None
        self._reqs_by_seq: ta.Dict[int, RemoteCommandExecutor._Request] = {}

    #

    async def start(self) -> None:
        check_none(self._loop_task)
        check_state(not self._stop.is_set())
        self._loop_task = asyncio.create_task(self._loop())

    async def aclose(self) -> None:
        self._stop.set()
        if self._loop_task is not None:
            await self._loop_task

    #

    @dc.dataclass(frozen=True)
    class _Request:
        seq: int
        cmd: Command
        fut: asyncio.Future

    async def _loop(self) -> None:
        stop_task = asyncio.create_task(self._stop.wait())
        queue_task: ta.Optional[asyncio.Task] = None
        recv_task: ta.Optional[asyncio.Task] = None

        while not self._stop.is_set():
            if queue_task is None:
                queue_task = asyncio.create_task(self._queue.get())
            if recv_task is None:
                recv_task = asyncio.create_task(_RemoteExecutionProtocol.Response.recv(self._chan))

            done, pending = await asyncio.wait([
                stop_task,
                queue_task,
                recv_task,
            ], return_when=asyncio.FIRST_COMPLETED)

            if queue_task in done:
                req = check_isinstance(queue_task.result(), RemoteCommandExecutor._Request)
                queue_task = None
                await self._handle_request(req)

            if recv_task in done:
                resp = check_isinstance(recv_task.result(), (_RemoteExecutionProtocol.Response, type(None)))
                recv_task = None
                await self._handle_response(resp)

        for task in [
            stop_task,
            queue_task,
            recv_task,
        ]:
            if task is not None and not task.done():
                task.cancel()

    async def _handle_request(self, req: _Request) -> None:
        self._reqs_by_seq[req.seq] = req

        await _RemoteExecutionProtocol.CommandRequest(
            seq=req.seq,
            cmd=req.cmd,
        ).send(self._chan)

    async def _handle_response(self, resp: ta.Optional[_RemoteExecutionProtocol.Response]) -> None:
        if resp is None:
            raise EOFError

        if isinstance(resp, _RemoteExecutionProtocol.LogResponse):
            log.info(resp.s)

        elif isinstance(resp, _RemoteExecutionProtocol.CommandResponse):
            req = self._reqs_by_seq.pop(resp.seq)
            req.fut.set_result(resp.res)

        else:
            raise TypeError(resp)

    #

    async def _remote_execute(self, cmd: Command) -> CommandOutputOrException:
        req = RemoteCommandExecutor._Request(
            seq=next(self._cmd_seq),
            cmd=cmd,
            fut=asyncio.Future(),
        )

        await self._queue.put(req)

        return await req.fut

    # @ta.override
    async def execute(self, cmd: Command) -> Command.Output:
        r = await self._remote_execute(cmd)
        if (e := r.exception) is not None:
            raise RemoteCommandError(e)
        else:
            return check_not_none(r.output)

    # @ta.override
    async def try_execute(
            self,
            cmd: Command,
            *,
            log: ta.Optional[logging.Logger] = None,
            omit_exc_object: bool = False,
    ) -> CommandOutputOrException:
        try:
            r = await self._remote_execute(cmd)

        except Exception as e:  # noqa
            if log is not None:
                log.exception('Exception executing remote command: %r', type(cmd))

            return CommandOutputOrExceptionData(exception=CommandException.of(
                e,
                omit_exc_object=omit_exc_object,
                cmd=cmd,
            ))

        else:
            return r
