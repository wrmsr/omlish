# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - can implement sched w/ select
"""
import dataclasses as dc
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers
from omlish.logs.modules import get_module_loggers

from ..core import ChannelPipelineMessages
from ..core import PipelineChannel


log, alog = get_module_loggers(globals())  # noqa


##


class SyncSocketPipelineChannelDriver:
    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['SyncSocketPipelineChannelDriver.Config']

        read_chunk_size: int = 0x10000
        write_chunk_max: ta.Optional[int] = None

    Config.DEFAULT = Config()

    #

    def __init__(
            self,
            spec: PipelineChannel.Spec,
            sock: ta.Any,
            config: ta.Optional[Config] = None,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._sock = sock
        if config is None:
            config = SyncSocketPipelineChannelDriver.Config.DEFAULT
        self._config = config

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> Config:
        return self._config

    _channel: PipelineChannel

    def _handle_output(self, msg: ta.Any) -> bool:
        if ByteStreamBuffers.can_bytes(msg):
            for mv in ByteStreamBuffers.iter_segments(msg):
                self._sock.send(mv)
            return True

        elif isinstance(msg, ChannelPipelineMessages.FinalOutput):
            return False

        else:
            raise TypeError(msg)

    def _run(self, in_msgs: ta.List[ta.Any]) -> None:
        try:
            self._channel  # noqa
        except AttributeError:
            pass
        else:
            raise RuntimeError('Already running')

        self._channel = PipelineChannel(self._spec)

        try:
            while True:
                if in_msgs:
                    self._channel.feed_in(*in_msgs)
                    in_msgs.clear()

                while (msg := self._channel.output.poll()) is not None:
                    if not self._handle_output(msg):
                        return

                b = self._sock.recv(self._config.read_chunk_size)
                if not b:
                    in_msgs.append(ChannelPipelineMessages.FinalInput())
                else:
                    in_msgs.append(b)

        finally:
            self._channel.destroy()

    def run(self, *in_msgs: ta.Any) -> None:
        self._run(list(in_msgs))
