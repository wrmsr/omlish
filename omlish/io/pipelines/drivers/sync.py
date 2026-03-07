# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - can implement sched w/ select
"""
import dataclasses as dc
import typing as ta

from ....io.streams.utils import ByteStreamBuffers
from ....logs.modules import get_module_loggers
from ..core import IoPipeline
from ..core import IoPipelineMessages


log, alog = get_module_loggers(globals())  # noqa


##


class SyncSocketIoPipelineDriver:
    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['SyncSocketIoPipelineDriver.Config']

        read_chunk_size: int = 64 * 1024
        write_chunk_max: ta.Optional[int] = None

    Config.DEFAULT = Config()

    #

    def __init__(
            self,
            spec: IoPipeline.Spec,
            sock: ta.Any,
            config: ta.Optional[Config] = None,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._sock = sock
        if config is None:
            config = SyncSocketIoPipelineDriver.Config.DEFAULT
        self._config = config

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

    _channel: IoPipeline

    def _handle_output(self, msg: ta.Any) -> bool:
        """Returns whether or not to continue running."""

        if ByteStreamBuffers.can_bytes(msg):
            for mv in ByteStreamBuffers.iter_segments(msg):
                self._sock.send(mv)
            return True

        elif isinstance(msg, IoPipelineMessages.FinalOutput):
            return False

        elif isinstance(msg, IoPipelineMessages.Defer):
            self._channel.run_deferred(msg)
            return True

        else:
            raise TypeError(msg)

    def _run(self, in_msgs: ta.List[ta.Any]) -> None:
        try:
            self._channel  # noqa
        except AttributeError:
            pass
        else:
            raise RuntimeError('Already running')

        self._channel = IoPipeline(self._spec)

        try:
            self._channel.feed_initial_input()

            while True:
                if in_msgs:
                    self._channel.feed_in(*in_msgs)
                    in_msgs.clear()

                while (msg := self._channel.output.poll()) is not None:
                    if not self._handle_output(msg):
                        return

                if not self._channel.saw_final_input:
                    b = self._sock.recv(self._config.read_chunk_size)
                    if not b:
                        in_msgs.append(IoPipelineMessages.FinalInput())
                    else:
                        in_msgs.append(b)

        finally:
            self._channel.destroy()

    def run(self, *in_msgs: ta.Any) -> None:
        self._run(list(in_msgs))
