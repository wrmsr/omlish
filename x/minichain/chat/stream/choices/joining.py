import typing as ta

from omlish import check

from ...messages import AiChat
from ...stream.joining import AiDeltaJoiner
from .types import AiChoiceDeltas


##


class AiChoicesDeltaJoiner:
    def __init__(self) -> None:
        super().__init__()

        self._seq = 0
        self._channels: list[AiDeltaJoiner] = []

    def add(self, choices: ta.Sequence[AiChoiceDeltas]) -> None:
        if not self._seq:
            check.empty(self._channels)
            self._channels.extend(AiDeltaJoiner() for _ in range(len(choices)))

        for chan, c in zip(self._channels, choices, strict=True):
            chan.add(c.deltas)

        self._seq += 1

    def build(self) -> list[AiChat]:
        return [list(chan.build()) for chan in self._channels]
