# ruff: noqa: UP006 UP007
import abc
import asyncio
import contextlib
import dataclasses as dc
import itertools
import logging
import sys
import typing as ta

from omlish.lite.asyncio.asyncio import asyncio_open_stream_reader
from omlish.lite.asyncio.asyncio import asyncio_open_stream_writer
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_isinstance
from omlish.lite.check import check_none
from omlish.lite.check import check_not_none
from omlish.lite.check import check_state
from omlish.lite.logs import log
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect

from ...pyremote import PyremoteBootstrapDriver
from ...pyremote import PyremoteBootstrapOptions
from ...pyremote import pyremote_bootstrap_finalize
from ...pyremote import pyremote_build_bootstrap_cmd
from ..bootstrap import MainBootstrap
from ..commands.base import Command
from ..commands.base import CommandException
from ..commands.base import CommandExecutor
from ..commands.base import CommandOutputOrException
from ..commands.base import CommandOutputOrExceptionData
from ..commands.execution import LocalCommandExecutor
from .channel import RemoteChannel
from .payload import RemoteExecutionPayloadFile
from .payload import get_remote_payload_src
from .spawning import RemoteSpawning


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


class _RemoteExecutionLogHandler(logging.Handler):
    def __init__(self, fn: ta.Callable[[str], None]) -> None:
        super().__init__()
        self._fn = fn

    def emit(self, record):
        msg = self.format(record)
        self._fn(msg)


async def _async_remote_execution_main(
        input: asyncio.StreamReader,  # noqa
        output: asyncio.StreamWriter,
) -> None:
    async with contextlib.AsyncExitStack() as es:  # noqa
        chan = RemoteChannel(
            input,
            output,
        )

        bs = check_not_none(await chan.recv_obj(MainBootstrap))

        if (prd := bs.remote_config.pycharm_remote_debug) is not None:
            pycharm_debug_connect(prd)

        injector = main_bootstrap(bs)

        chan.set_marshaler(injector[ObjMarshalerManager])

        #

        def log_fn(s: str) -> None:
            # async def inner():
            #     await _RemoteExecutionProtocol.LogResponse(s).send(chan)
            #
            # loop = asyncio.get_running_loop()
            # if loop is not None:
            #     asyncio.run_coroutine_threadsafe(inner(), loop)
            pass

        log_handler = _RemoteExecutionLogHandler(log_fn)
        logging.root.addHandler(log_handler)

        #

        ce = injector[LocalCommandExecutor]

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
            ).send(chan)

            cmd_futs_by_seq.pop(req.seq)  # noqa

        while True:
            sys.stderr.write('loop entered\n')

            req = await _RemoteExecutionProtocol.Request.recv(chan)
            if req is None:
                break

            sys.stderr.write(repr(req) + '\n')

            if isinstance(req, _RemoteExecutionProtocol.CommandRequest):
                fut = asyncio.create_task(handle_cmd(req))
                cmd_futs_by_seq[req.seq] = fut

            else:
                raise TypeError(req)

        sys.stderr.write('loop exited\n')


def _remote_execution_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    async def inner() -> None:
        sys.stderr.write(f'{rt.input.fileno()=}')
        sys.stderr.write(f'{rt.output.fileno()=}')
        input = await asyncio_open_stream_reader(rt.input)  # noqa
        output = await asyncio_open_stream_writer(rt.output)

        await _async_remote_execution_main(
            input,
            output,
        )

    try:
        asyncio.run(inner())
    except Exception as exc:
        sys.stderr.write(repr(exc) + '\n')
        raise


##


@dc.dataclass()
class RemoteCommandError(Exception):
    e: CommandException


class RemoteCommandExecutor(CommandExecutor):
    def __init__(self, chan: RemoteChannel) -> None:
        super().__init__()

        self._chan = chan
        self._cmd_seq = itertools.count()
        self._queue: asyncio.Queue = asyncio.Queue()
        self._stop = asyncio.Event()
        self._loop_task: ta.Optional[asyncio.Task] = None

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

        reqs_by_seq: ta.Dict[int, RemoteCommandExecutor._Request] = {}

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

                reqs_by_seq[req.seq] = req

                await _RemoteExecutionProtocol.CommandRequest(
                    seq=req.seq,
                    cmd=req.cmd,
                ).send(self._chan)

            if recv_task in done:
                resp = check_isinstance(recv_task.result(), _RemoteExecutionProtocol.Response)
                recv_task = None

                if resp is None:
                    raise EOFError

                if isinstance(resp, _RemoteExecutionProtocol.LogResponse):
                    log.info(resp.s)

                elif isinstance(resp, _RemoteExecutionProtocol.CommandResponse):
                    req = reqs_by_seq.pop(resp.seq)
                    req.fut.set_result(resp.res)

                else:
                    raise TypeError(resp)

        for task in [
            stop_task,
            queue_task,
            recv_task,
        ]:
            if task is not None and not task.done():
                task.cancel()

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


##


class RemoteExecution:
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

            chan = RemoteChannel(
                proc.stdout,
                proc.stdin,
                msh=self._msh,
            )

            await chan.send_obj(bs)

            rce: RemoteCommandExecutor
            async with contextlib.aclosing(RemoteCommandExecutor(chan)) as rce:
                await rce.start()

                yield rce
