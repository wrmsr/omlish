import typing as ta

from omlish import check

from ...tools.types import ToolUse
from ..choices.types import AiChoice
from ..messages import AiMessage
from ..messages import AiChat
from ..messages import AnyAiMessage
from ..messages import ToolUseMessage
from .types import AiChoiceDelta
from .types import AiChoiceDeltas
from .types import ContentAiChoiceDelta
from .types import ToolUseAiChoiceDelta


##


class AiChoiceDeltaJoiner:
    def __init__(self) -> None:
        super().__init__()

        self._seq = 0
        self._channels: list[AiChoiceDeltaJoiner._Channel] = []

    class _Channel(ta.NamedTuple):
        deltas: list[AiChoiceDelta]
        messages: list[AnyAiMessage]

    def _build_joined(self, deltas: ta.Sequence[AiChoiceDelta]) -> AnyAiMessage:
        dty = check.single(set(map(type, deltas)))

        if dty is ContentAiChoiceDelta:
            return AiMessage(''.join(check.isinstance(ta.cast(ContentAiChoiceDelta, d).c, str) for d in deltas))

        else:
            raise TypeError(dty)

    def _join_one(self, chan: _Channel) -> None:
        if not chan.deltas:
            return

        chan.messages.append(self._build_joined(chan.deltas))
        chan.deltas.clear()

    def _add_to(self, chan: _Channel, d: AiChoiceDelta) -> None:
        if chan.deltas and type(chan.deltas[0]) is not type(d):
            self._join_one(chan)

        chan.deltas.append(d)

    def add(self, choices: ta.Sequence[AiChoiceDeltas]) -> None:
        l: list[list[str] | ToolUse]

        if not self._seq:
            check.empty(self._channels)
            self._channels.extend(self._Channel([], []) for _ in range(len(choices)))

        for chan, c in zip(self._channels, choices, strict=True):
            for d in c.deltas:
                self._add_to(chan, d)

        self._seq += 1

    def build(self) -> list[AiChat]:
        for chan in self._channels:
            self._join_one(chan)

        return [list(chan.messages) for chan in self._channels]
