# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from ...core import ChannelPipelineHandler


##


class CoroChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    class Error(Exception):
        pass

    class NotStartedError(Error):
        pass

    class ClosedError(Error):
        pass

    #

    @ta.final
    class _Runner:
        """Analogous to `omlish.funcs.genmachine`."""

        def __init__(self, initial: ta.Any) -> None:
            self._gen = initial

            if (n := next(self._gen)) is not None:
                raise CoroChannelPipelineHandler.NotStartedError
            check.none(n)

        _gen: ta.Optional[ta.Any]

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}@{id(self):x}<{self.state}>'

        @property
        def state(self) -> ta.Optional[str]:
            if self._gen is not None:
                return self._gen.gi_code.co_qualname
            return None

        @property
        def closed(self) -> bool:
            return self._gen is None

        def close(self) -> None:
            if self._gen is not None:
                self._gen.close()
                self._gen = None

        def feed(self, i: ta.Any) -> ta.Iterator[ta.Any]:
            if self._gen is None:
                raise CoroChannelPipelineHandler.ClosedError

            gi: ta.Optional[ta.Any] = i
            while True:
                try:
                    while (o := self._gen.send(gi)) is not None:
                        gi = None
                        yield from o

                    break

                except StopIteration as s:
                    if (sv := s.value) is None:
                        self._gen = None
                        return

                    self._gen = sv
                    gi = None
