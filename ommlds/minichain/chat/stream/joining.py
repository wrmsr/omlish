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

        self._all: list[AiDelta] = []
        self._queue: list[AiDelta] = []
        self._out: list[AnyAiMessage] = []

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

            if not ra:
                ra = '{}'

            return ToolUseMessage(ToolUse(
                id=tds[0].id,
                name=check.non_empty_str(tds[0].name),
                args=json.loads(ra),
                raw_args=ra,
            ))

        else:
            raise TypeError(dty)

    def _join(self) -> None:
        if not self._queue:
            return

        self._out.append(self._build_joined(self._queue))
        self._queue.clear()

    def _should_join(self, *, new: AiDelta | None = None) -> bool:
        if not self._queue:
            return False

        if new is not None and type(self._queue[0]) is not type(new):
            return True

        if (
                isinstance(d0 := self._queue[0], PartialToolUseAiDelta) and
                isinstance(new, PartialToolUseAiDelta) and
                d0.id is not None and
                new.id is not None and
                d0.id != new.id
        ):
            return True

        return False

    def _add_one(self, d: AiDelta) -> None:
        if self._should_join(new=d):
            self._join()

        self._all.append(d)

        if isinstance(d, ToolUseAiDelta):
            self._out.append(ToolUseMessage(ToolUse(
                id=d.id,
                name=check.not_none(d.name),
                args=d.args or {},
                raw_args=json.dumps_compact(d.args),
            )))

        else:
            self._queue.append(d)

    def add(self, deltas: AiDeltas) -> None:
        for d in deltas:
            self._add_one(d)

    def build(self) -> AiChat:
        self._join()

        return list(self._out)
