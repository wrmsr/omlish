# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - can implement sched w/ select
"""
import collections
import dataclasses as dc
import typing as ta

from ....io.streams.utils import ByteStreamBuffers
from ....logs.modules import get_module_loggers
from ..core import IoPipeline
from ..core import IoPipelineMessages
from .metadata import DriverIoPipelineMetadata


BaseSyncSocketIoPipelineDriverConfigT = ta.TypeVar('BaseSyncSocketIoPipelineDriverConfigT', bound='BaseSyncSocketIoPipelineDriver.Config')  # noqa


log, alog = get_module_loggers(globals())  # noqa


##


class BaseSyncSocketIoPipelineDriver(ta.Generic[BaseSyncSocketIoPipelineDriverConfigT]):
    @dc.dataclass(frozen=True)
    class Config:
        read_chunk_size: int = 64 * 1024
        write_chunk_max: ta.Optional[int] = None

    #

    def __init__(
            self,
            spec: IoPipeline.Spec,
            sock: ta.Any,
            config: BaseSyncSocketIoPipelineDriverConfigT,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._sock = sock
        self._config = config

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}'

    @property
    def config(self) -> BaseSyncSocketIoPipelineDriverConfigT:
        return self._config

    #

    _pipeline_: IoPipeline

    def _pipeline(self) -> ta.Optional[IoPipeline]:
        try:
            return self._pipeline_
        except AttributeError:
            return None

    def _ensure_pipeline(self) -> IoPipeline:
        try:
            return self._pipeline_
        except AttributeError:
            pass
        self._pipeline_ = pipeline = self._make_pipeline()
        return pipeline

    def _make_pipeline(self) -> IoPipeline:
        return IoPipeline(dc.replace(
            self._spec,
            metadata=(*self._spec.metadata, DriverIoPipelineMetadata(self)),
        ))

    #

    def __enter__(self) -> 'BaseSyncSocketIoPipelineDriver':  # noqa
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (pipeline := self._pipeline()) is not None:
            pipeline.destroy()

    #

    def _handle_output(self, msg: ta.Any) -> bool:
        """Returns whether or not to continue running."""

        if ByteStreamBuffers.can_bytes(msg):
            for mv in ByteStreamBuffers.iter_segments(msg):
                self._sock.send(mv)
            return True

        elif isinstance(msg, IoPipelineMessages.FinalOutput):
            return False

        elif isinstance(msg, IoPipelineMessages.Defer):
            self._pipeline_.run_deferred(msg)
            return True

        else:
            raise TypeError(msg)


##


class LoopSyncSocketIoPipelineDriver(BaseSyncSocketIoPipelineDriver['LoopSyncSocketIoPipelineDriver.Config']):
    @dc.dataclass(frozen=True)
    class Config(BaseSyncSocketIoPipelineDriver.Config):
        DEFAULT: ta.ClassVar['LoopSyncSocketIoPipelineDriver.Config']

    Config.DEFAULT = Config()

    #

    def __init__(
            self,
            spec: IoPipeline.Spec,
            sock: ta.Any,
            config: ta.Optional[Config] = None,
    ) -> None:
        super().__init__(spec, sock, config or LoopSyncSocketIoPipelineDriver.Config.DEFAULT)

    #

    def __enter__(self) -> 'LoopSyncSocketIoPipelineDriver':  # noqa
        return self

    #

    def _run(self, in_msgs: ta.List[ta.Any]) -> None:
        if self._pipeline() is not None:
            raise RuntimeError('Already running')

        pipeline = self._ensure_pipeline()

        try:
            pipeline.feed_initial_input()

            while True:
                if in_msgs:
                    pipeline.feed_in(*in_msgs)
                    in_msgs.clear()

                while (msg := pipeline.output.poll()) is not None:
                    if not self._handle_output(msg):
                        return

                if not pipeline.saw_final_input:
                    b = self._sock.recv(self._config.read_chunk_size)
                    if not b:
                        in_msgs.append(IoPipelineMessages.FinalInput())
                    else:
                        in_msgs.append(b)

        finally:
            pipeline.destroy()

    def run(self, *in_msgs: ta.Any) -> None:
        self._run(list(in_msgs))


##


class IterSyncSocketIoPipelineDriver(BaseSyncSocketIoPipelineDriver['IterSyncSocketIoPipelineDriver.Config']):
    @dc.dataclass(frozen=True)
    class Config(BaseSyncSocketIoPipelineDriver.Config):
        DEFAULT: ta.ClassVar['IterSyncSocketIoPipelineDriver.Config']

    #

    def __init__(
            self,
            spec: IoPipeline.Spec,
            sock: ta.Any,
            config: ta.Optional[Config] = None,
    ) -> None:
        super().__init__(spec, sock, config or self.Config.DEFAULT)

        self._input_q: collections.deque[ta.Any] = collections.deque()
        self._input_q.append(IoPipelineMessages.InitialInput())

    #

    def __enter__(self) -> 'IterSyncSocketIoPipelineDriver':  # noqa
        return self

    #

    def enqueue(self, *in_msgs: ta.Any) -> None:
        self._input_q.extend(in_msgs)

    def next(self) -> ta.Optional[ta.Any]:
        pipeline = self._ensure_pipeline()  # noqa

        raise NotImplementedError
