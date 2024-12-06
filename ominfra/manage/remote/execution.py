# ruff: noqa: UP006 UP007
import dataclasses as dc
import logging
import typing as ta

from omlish.lite.check import check_not_none
from omlish.lite.logs import log
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import PycharmRemoteDebug
from omlish.lite.pycharm import pycharm_debug_connect

from ...pyremote import pyremote_bootstrap_finalize
from ..bootstrap import MainBootstrap
from ..bootstrap import main_bootstrap
from ..commands.base import Command
from ..commands.base import CommandException
from ..commands.base import CommandExecutor
from ..commands.base import CommandOutputOrException
from ..commands.base import CommandOutputOrExceptionData
from .channel import RemoteChannel


@dc.dataclass(frozen=True)
class RemoteExecutionContext:
    main_bootstrap: MainBootstrap

    pycharm_remote_debug: ta.Optional[PycharmRemoteDebug] = None


def _remote_execution_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    chan = RemoteChannel(
        rt.input,
        rt.output,
    )

    ctx = check_not_none(chan.recv_obj(RemoteExecutionContext))

    #

    if (prd := ctx.pycharm_remote_debug) is not None:
        pycharm_debug_connect(prd)

    #

    injector = main_bootstrap(ctx.main_bootstrap)

    #

    chan.set_marshaler(injector[ObjMarshalerManager])

    #

    ce = injector[CommandExecutor]

    #

    while True:
        i = chan.recv_obj(Command)
        if i is None:
            break

        r = ce.try_execute(
            i,
            log=log,
            omit_exc_object=True,
        )

        chan.send_obj(r)


@dc.dataclass()
class RemoteCommandError(Exception):
    e: CommandException


class RemoteCommandExecutor(CommandExecutor):
    def __init__(self, chan: RemoteChannel) -> None:
        super().__init__()

        self._chan = chan

    def _remote_execute(self, cmd: Command) -> CommandOutputOrException:
        self._chan.send_obj(cmd, Command)

        if (r := self._chan.recv_obj(CommandOutputOrExceptionData)) is None:
            raise EOFError

        return r

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
