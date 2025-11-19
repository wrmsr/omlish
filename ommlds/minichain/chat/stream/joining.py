import typing as ta

from omlish import check
from omlish.formats import json

from ...tools.types import ToolUse
from ..messages import AiChat
from ..messages import AiMessage
from ..messages import AnyAiMessage
from ..messages import ToolUseMessage
from .types import AiDelta
from .types import AiDeltas
from .types import ContentAiDelta
from .types import PartialToolUseAiDelta
from .types import ToolUseAiDelta


##


class AiDeltaJoiner:
    def __init__(self) -> None:
        super().__init__()

        self._deltas: list[AiDelta] = []
        self._messages: list[AnyAiMessage] = []

    def _build_joined(self, deltas: ta.Sequence[AiDelta]) -> AnyAiMessage:
        dty = check.single(set(map(type, check.not_empty(deltas))))

        if dty is ContentAiDelta:
            cds = ta.cast(ta.Sequence[ContentAiDelta], deltas)
            return AiMessage(''.join(check.isinstance(cd.c, str) for cd in cds))

        elif dty is ToolUseAiDelta:
            raise TypeError(dty)

        elif dty is PartialToolUseAiDelta:
            tds = ta.cast(ta.Sequence[PartialToolUseAiDelta], deltas)
            for td in ta.cast(ta.Sequence[PartialToolUseAiDelta], deltas)[1:]:
                check.none(td.id)
                check.none(td.name)

            ra = ''.join(filter(None, (td.raw_args for td in tds)))

            return ToolUseMessage(ToolUse(
                id=tds[0].id,
                name=check.non_empty_str(tds[0].name),
                args=json.loads(ra),
                raw_args=ra,
            ))

        else:
            raise TypeError(dty)

    def _maybe_join(self) -> None:
        if not self._deltas:
            return

        self._messages.append(self._build_joined(self._deltas))
        self._deltas.clear()

    def _add_one(self, d: AiDelta) -> None:
        if self._deltas and type(self._deltas[0]) is not type(d):
            self._maybe_join()

        if isinstance(d, ToolUseAiDelta):
            self._messages.append(ToolUseMessage(ToolUse(
                id=d.id,
                name=check.not_none(d.name),
                args=d.args or {},
                raw_args=json.dumps_compact(d.args),
            )))

        else:
            self._deltas.append(d)

    def add(self, deltas: AiDeltas) -> None:
        for d in deltas:
            self._add_one(d)

    def build(self) -> AiChat:
        self._maybe_join()

        return list(self._messages)
