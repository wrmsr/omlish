# ruff: noqa: UP006 UP007
import dataclasses as dc
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
from ..commands.base import CommandExecutor
from .channel import RemoteChannel


@dc.dataclass(frozen=True)
class RemoteContext:
    main_bootstrap: MainBootstrap

    pycharm_remote_debug: ta.Optional[PycharmRemoteDebug] = None


def _remote_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    chan = RemoteChannel(
        rt.input,
        rt.output,
    )

    ctx = check_not_none(chan.recv_obj(RemoteContext))

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
