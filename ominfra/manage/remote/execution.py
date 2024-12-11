# ruff: noqa: UP006 UP007
"""
TODO:
 - sequence all messages
"""
import abc
import asyncio
import dataclasses as dc
import itertools
import logging
import time
import typing as ta

from omlish.lite.check import check
from omlish.lite.logs import log

from ..commands.base import Command
from ..commands.base import CommandException
from ..commands.base import CommandExecutor
from ..commands.base import CommandOutputOrException
from ..commands.base import CommandOutputOrExceptionData
from .channel import RemoteChannel


T = ta.TypeVar('T')


##


class _RemoteProtocol:
    class Message(abc.ABC):  # noqa
        async def send(self, chan: RemoteChannel) -> None:
            await chan.send_obj(self, _RemoteProtocol.Message)

        @classmethod
        async def recv(cls: ta.Type[T], chan: RemoteChannel) -> ta.Optional[T]:
            return await chan.recv_obj(cls)

    #

    class Request(Message, abc.ABC):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class CommandRequest(Request):
        seq: int
        cmd: Command

    @dc.dataclass(frozen=True)
    class PingRequest(Request):
        time: float

    #

    class Response(Message, abc.ABC):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class LogResponse(Response):
        s: str

    @dc.dataclass(frozen=True)
    class CommandResponse(Response):
        seq: int
        res: CommandOutputOrExceptionData

    @dc.dataclass(frozen=True)
    class PingResponse(Response):
        time: float


##


class _RemoteLogHandler(logging.Handler):
    def __init__(
            self,
            chan: RemoteChannel,
            loop: ta.Any = None,
    ) -> None:
        super().__init__()

        self._chan = chan
        self._loop = loop

    def emit(self, record):
        msg = self.format(record)

        async def inner():
            await _RemoteProtocol.LogResponse(msg).send(self._chan)

        loop = self._loop
        if loop is None:
            loop = asyncio.get_running_loop()
        if loop is not None:
            asyncio.run_coroutine_threadsafe(inner(), loop)


##


class _RemoteCommandHandler:
    DEFAULT_PING_INTERVAL_S: float = 3.

    def __init__(
            self,
            chan: RemoteChannel,
            executor: CommandExecutor,
            *,
            stop: ta.Optional[asyncio.Event] = None,
            ping_interval_s: float = DEFAULT_PING_INTERVAL_S,
    ) -> None:
        super().__init__()

        self._chan = chan
        self._executor = executor
        self._stop = stop if stop is not None else asyncio.Event()
        self._ping_interval_s = ping_interval_s

        self._cmds_by_seq: ta.Dict[int, _RemoteCommandHandler._Command] = {}

        self._last_ping_send: float = 0.
        self._ping_in_flight: bool = False
        self._last_ping_recv: ta.Optional[float] = None

    def stop(self) -> None:
        self._stop.set()

    @dc.dataclass(frozen=True)
    class _Command:
        req: _RemoteProtocol.CommandRequest
        fut: asyncio.Future

    async def run(self) -> None:
        log.debug('_RemoteCommandHandler loop start: %r', self)

        stop_task = asyncio.create_task(self._stop.wait())
        recv_task: ta.Optional[asyncio.Task] = None

        while not self._stop.is_set():
            if recv_task is None:
                recv_task = asyncio.create_task(_RemoteProtocol.Message.recv(self._chan))

            if not self._ping_in_flight:
                if not self._last_ping_recv:
                    ping_wait_time = 0.
                else:
                    ping_wait_time = self._ping_interval_s - (time.time() - self._last_ping_recv)
            else:
                ping_wait_time = float('inf')
            wait_time = min(self._ping_interval_s, ping_wait_time)
            log.debug('_RemoteCommandHandler loop wait: %f', wait_time)

            done, pending = await asyncio.wait(
                [
                    stop_task,
                    recv_task,
                ],
                return_when=asyncio.FIRST_COMPLETED,
                timeout=wait_time,
            )

            #

            if (
                    (time.time() - self._last_ping_send >= self._ping_interval_s) and
                    not self._ping_in_flight
            ):
                now = time.time()
                self._last_ping_send = now
                self._ping_in_flight = True
                await _RemoteProtocol.PingRequest(
                    time=now,
                ).send(self._chan)

            #

            if recv_task in done:
                msg: ta.Optional[_RemoteProtocol.Message] = check.isinstance(
                    recv_task.result(),
                    (_RemoteProtocol.Message, type(None)),
                )
                recv_task = None

                if msg is None:
                    break

                await self._handle_message(msg)

        log.debug('_RemoteCommandHandler loop stopping: %r', self)

        for task in [
            stop_task,
            recv_task,
        ]:
            if task is not None and not task.done():
                task.cancel()

        for cmd in self._cmds_by_seq.values():
            cmd.fut.cancel()

        log.debug('_RemoteCommandHandler loop exited: %r', self)

    async def _handle_message(self, msg: _RemoteProtocol.Message) -> None:
        if isinstance(msg, _RemoteProtocol.PingRequest):
            log.debug('Ping: %r', msg)
            await _RemoteProtocol.PingResponse(
                time=msg.time,
            ).send(self._chan)

        elif isinstance(msg, _RemoteProtocol.PingResponse):
            latency_s = time.time() - msg.time
            log.debug('Pong: %0.2f ms %r', latency_s * 1000., msg)
            self._last_ping_recv = time.time()
            self._ping_in_flight = False

        elif isinstance(msg, _RemoteProtocol.CommandRequest):
            fut = asyncio.create_task(self._handle_command_request(msg))
            self._cmds_by_seq[msg.seq] = _RemoteCommandHandler._Command(
                req=msg,
                fut=fut,
            )

        else:
            raise TypeError(msg)

    async def _handle_command_request(self, req: _RemoteProtocol.CommandRequest) -> None:
        res = await self._executor.try_execute(
            req.cmd,
            log=log,
            omit_exc_object=True,
        )

        await _RemoteProtocol.CommandResponse(
            seq=req.seq,
            res=CommandOutputOrExceptionData(
                output=res.output,
                exception=res.exception,
            ),
        ).send(self._chan)

        self._cmds_by_seq.pop(req.seq)  # noqa


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
        check.none(self._loop_task)
        check.state(not self._stop.is_set())
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
        log.debug('RemoteCommandExecutor loop start: %r', self)

        stop_task = asyncio.create_task(self._stop.wait())
        queue_task: ta.Optional[asyncio.Task] = None
        recv_task: ta.Optional[asyncio.Task] = None

        while not self._stop.is_set():
            if queue_task is None:
                queue_task = asyncio.create_task(self._queue.get())
            if recv_task is None:
                recv_task = asyncio.create_task(_RemoteProtocol.Message.recv(self._chan))

            done, pending = await asyncio.wait(
                [
                    stop_task,
                    queue_task,
                    recv_task,
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            #

            if queue_task in done:
                req = check.isinstance(queue_task.result(), RemoteCommandExecutor._Request)
                queue_task = None
                await self._handle_queued_request(req)

            #

            if recv_task in done:
                msg: ta.Optional[_RemoteProtocol.Message] = check.isinstance(
                    recv_task.result(),
                    (_RemoteProtocol.Message, type(None)),
                )
                recv_task = None

                if msg is None:
                    log.debug('RemoteCommandExecutor got eof: %r', self)
                    break

                await self._handle_message(msg)

        log.debug('RemoteCommandExecutor loop stopping: %r', self)

        for task in [
            stop_task,
            queue_task,
            recv_task,
        ]:
            if task is not None and not task.done():
                task.cancel()

        for req in self._reqs_by_seq.values():
            req.fut.cancel()

        log.debug('RemoteCommandExecutor loop exited: %r', self)

    async def _handle_queued_request(self, req: _Request) -> None:
        self._reqs_by_seq[req.seq] = req
        await _RemoteProtocol.CommandRequest(
            seq=req.seq,
            cmd=req.cmd,
        ).send(self._chan)

    async def _handle_message(self, msg: _RemoteProtocol.Message) -> None:
        if isinstance(msg, _RemoteProtocol.PingRequest):
            log.debug('Ping: %r', msg)
            await _RemoteProtocol.PingResponse(
                time=msg.time,
            ).send(self._chan)

        elif isinstance(msg, _RemoteProtocol.PingResponse):
            latency_s = time.time() - msg.time
            log.debug('Pong: %0.2f ms %r', latency_s * 1000., msg)

        elif isinstance(msg, _RemoteProtocol.LogResponse):
            log.info(msg.s)

        elif isinstance(msg, _RemoteProtocol.CommandResponse):
            req = self._reqs_by_seq.pop(msg.seq)
            req.fut.set_result(msg.res)

        else:
            raise TypeError(msg)

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
            return check.not_none(r.output)

    # @ta.override
    async def try_execute(
            self,
            cmd: Command,
            *,
            log: ta.Optional[logging.Logger] = None,  # noqa
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
