import itertools
import sys
import time
import typing as ta

import anyio.abc
import anyio.streams.stapled

from omlish.asyncs import anyio as aiu

from .types import Pid
from .types import Process
from .types import ProcessBehavior
from .types import ProcessMailbox
from .types import ProcessOptions
from .types import ProcessState
from .types import Node
from .types import MailboxMessage


##


class ProcessImpl(Process):
    def __init__(
            self,
            node: 'NodeImpl',
            pid: Pid,
            behavior: ProcessBehavior,
            mailbox: ProcessMailbox,
    ) -> None:
        super().__init__()
        self._node = node
        self._pid = pid
        self._behavior = behavior
        self._mailbox = mailbox

        self._state = ProcessState.INIT

    @property
    def pid(self) -> Pid:
        return self._pid

    @property
    def behavior(self) -> ProcessBehavior:
        return self._behavior

    @property
    def mailbox(self) -> ProcessMailbox:
        return self._mailbox

    @property
    def state(self) -> ProcessState:
        return self._state

    async def _run(self) -> None:
        if self._state != ProcessState.SLEEP:
            return
        self._state = ProcessState.RUN

        async def _inner():
            while True:
                await self._behavior.process_run()

                if self._state != ProcessState.RUN:
                    raise Exception('Killed')
                self._state = ProcessState.SLEEP

                if not self._mailbox.main.receive_stream.statistics().current_buffer_used:
                    break

                if self._state != ProcessState.SLEEP:
                    break
                self._state = ProcessState.RUN


        self._node._tg.start_soon(_inner)  # noqa


##


class NodeImpl(Node):
    def __init__(
            self,
            tg: anyio.abc.TaskGroup,
    ) -> None:
        super().__init__()

        self._tg = tg

        self._processes: dict[Pid, ProcessImpl] = {}
        self._id_seq = itertools.count()

        self._core_pid = self._next_pid()

    def _next_pid(self) -> Pid:
        return Pid(
            next(self._id_seq),
            int(time.monotonic()),
        )

    async def spawn(
            self,
            behavior_fac: ta.Callable[[], ProcessBehavior],
            opts: ProcessOptions = ProcessOptions(),
    ) -> Pid:
        pid = self._next_pid()

        behavior = behavior_fac()

        mailbox = ProcessMailbox(
            aiu.create_stapled_memory_object_stream(opts.mailbox_size or sys.maxsize),
        )

        proc = ProcessImpl(
            self,
            pid,
            behavior,
            mailbox,
        )

        await behavior.process_init(proc)

        proc._state = ProcessState.SLEEP  # noqa
        self._processes[pid] = proc

        await proc._run()  # noqa

        return proc.pid

    async def send(self, dst: Pid, msg: ta.Any) -> None:
        proc = self._processes[dst]
        if not proc.state.alive:
            raise Exception(f'terminated: {dst}')

        mbm = MailboxMessage(
            self._core_pid,
            msg,
        )
        try:
            proc.mailbox.main.send_stream.send_nowait(mbm)
        except anyio.WouldBlock:
            raise Exception('mailbox full')

        await proc._run()  # noqa
