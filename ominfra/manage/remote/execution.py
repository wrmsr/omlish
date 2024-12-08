# ruff: noqa: UP006 UP007
import contextlib
import dataclasses as dc
import logging
import threading
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_not_none
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


##


class _RemoteExecutionLogHandler(logging.Handler):
    def __init__(self, fn: ta.Callable[[str], None]) -> None:
        super().__init__()
        self._fn = fn

    def emit(self, record):
        msg = self.format(record)
        self._fn(msg)


@dc.dataclass(frozen=True)
class _RemoteExecutionRequest:
    c: Command


@dc.dataclass(frozen=True)
class _RemoteExecutionLog:
    s: str


@dc.dataclass(frozen=True)
class _RemoteExecutionResponse:
    r: ta.Optional[CommandOutputOrExceptionData] = None
    l: ta.Optional[_RemoteExecutionLog] = None


def _remote_execution_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    chan = RemoteChannel(
        rt.input,
        rt.output,
    )

    bs = check_not_none(chan.recv_obj(MainBootstrap))

    if (prd := bs.remote_config.pycharm_remote_debug) is not None:
        pycharm_debug_connect(prd)

    injector = main_bootstrap(bs)

    chan.set_marshaler(injector[ObjMarshalerManager])

    #

    log_lock = threading.RLock()
    send_logs = False

    def log_fn(s: str) -> None:
        with log_lock:
            if send_logs:
                chan.send_obj(_RemoteExecutionResponse(l=_RemoteExecutionLog(s)))

    log_handler = _RemoteExecutionLogHandler(log_fn)
    logging.root.addHandler(log_handler)

    #

    ce = injector[LocalCommandExecutor]

    while True:
        req = chan.recv_obj(_RemoteExecutionRequest)
        if req is None:
            break

        with log_lock:
            send_logs = True

        r = ce.try_execute(
            req.c,
            log=log,
            omit_exc_object=True,
        )

        with log_lock:
            send_logs = False

        chan.send_obj(_RemoteExecutionResponse(r=CommandOutputOrExceptionData(
            output=r.output,
            exception=r.exception,
        )))


##


@dc.dataclass()
class RemoteCommandError(Exception):
    e: CommandException


class RemoteCommandExecutor(CommandExecutor):
    def __init__(self, chan: RemoteChannel) -> None:
        super().__init__()

        self._chan = chan

    def _remote_execute(self, cmd: Command) -> CommandOutputOrException:
        self._chan.send_obj(_RemoteExecutionRequest(cmd))

        while True:
            if (r := self._chan.recv_obj(_RemoteExecutionResponse)) is None:
                raise EOFError

            if r.l is not None:
                log.info(r.l.s)

            if r.r is not None:
                return r.r

    # @ta.override
    def execute(self, cmd: Command) -> Command.Output:
        r = self._remote_execute(cmd)
        if (e := r.exception) is not None:
            raise RemoteCommandError(e)
        else:
            return check_not_none(r.output)

    # @ta.override
    def try_execute(
            self,
            cmd: Command,
            *,
            log: ta.Optional[logging.Logger] = None,
            omit_exc_object: bool = False,
    ) -> CommandOutputOrException:
        try:
            r = self._remote_execute(cmd)

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

    @contextlib.contextmanager
    def connect(
            self,
            tgt: RemoteSpawning.Target,
            bs: MainBootstrap,
    ) -> ta.Generator[RemoteCommandExecutor, None, None]:
        spawn_src = self._spawn_src()
        remote_src = self._remote_src()

        with self._spawning.spawn(
                tgt,
                spawn_src,
        ) as proc:
            res = PyremoteBootstrapDriver(  # noqa
                remote_src,
                PyremoteBootstrapOptions(
                    debug=bs.main_config.debug,
                ),
            ).run(
                proc.stdout,
                proc.stdin,
            )

            chan = RemoteChannel(
                proc.stdout,
                proc.stdin,
                msh=self._msh,
            )

            chan.send_obj(bs)

            yield RemoteCommandExecutor(chan)
