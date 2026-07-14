import typing as ta

from omcore import check
from omcore.formats.json import all as json

from ...tools.types import ToolUse
from ..messages import AiChat
from ..messages import AiMessage
from ..messages import AnyAiMessage
from ..messages import ThinkingMessage
from ..messages import ToolUseMessage
from ..metadata import MessageUuid
from ..metadata import ThoughtSignature
from .types import AiDelta
from .types import AiDeltas
from .types import ContentAiDelta
from .types import PartialToolUseAiDelta
from .types import ThinkingAiDelta
from .types import ToolUseAiDelta


##


class AiDeltaJoiner:
    def __init__(self) -> None:
        super().__init__()

        self._all: list[AiDelta] = []
        self._queue: list[AiDelta] = []
        self._out: list[AnyAiMessage] = []
        self._ptus_by_index: dict[int, list[PartialToolUseAiDelta]] = {}
        self._closed = False

    def _confer_uuid(self, m: AnyAiMessage, ds: ta.Sequence[AiDelta]) -> AnyAiMessage:
        dus = {du for d in ds if (du := d.metadata.get(MessageUuid)) is not None}
        if not dus:
            return m

        du = check.single(dus)

        if (mu := m.metadata.get(MessageUuid)) is not None:
            check.equal(du, mu)
            return m

        return m.with_metadata(du)

    def _build_joined(self, deltas: ta.Sequence[AiDelta]) -> AnyAiMessage:
        dty = check.single(set(map(type, check.not_empty(deltas))))

        if dty is ContentAiDelta:
            cds = ta.cast('ta.Sequence[ContentAiDelta]', deltas)

            aim = AiMessage(''.join(check.isinstance(cd.c, str) for cd in cds))

            return self._confer_uuid(aim, cds)

        elif dty is ThinkingAiDelta:
            ths = ta.cast('ta.Sequence[ThinkingAiDelta]', deltas)

            tm = ThinkingMessage(''.join(check.isinstance(th.c, str) for th in ths))

            return self._confer_uuid(tm, ths)

        elif dty is ToolUseAiDelta:
            raise TypeError(dty)

        elif dty is PartialToolUseAiDelta:
            tds = ta.cast('ta.Sequence[PartialToolUseAiDelta]', deltas)

            for td in ta.cast('ta.Sequence[PartialToolUseAiDelta]', deltas)[1:]:
                check.none(td.id)
                check.none(td.name)
                # check.none(td.index)  # FIXME

            ra = ''.join(filter(None, (td.raw_args for td in tds)))

            if not ra:
                ra = '{}'

            tum = ToolUseMessage(ToolUse(
                id=tds[0].id,
                name=check.non_empty_str(tds[0].name),
                args=json.loads(ra),
                raw_args=ra,
            ))

            return self._confer_uuid(tum, tds)

        else:
            raise TypeError(dty)

    def _join(self) -> None:
        if not self._queue:
            return

        self._out.append(self._build_joined(self._queue))
        self._queue.clear()

    def _join_indexed_ptus(self) -> None:
        if not self._ptus_by_index:
            return

        for ptus in self._ptus_by_index.values():
            self._out.append(self._build_joined(ptus))

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
        if isinstance(d, PartialToolUseAiDelta) and (ptu_idx := d.index) is not None:
            try:
                self._ptus_by_index[ptu_idx].append(d)
            except KeyError:
                self._ptus_by_index[ptu_idx] = [d]
            return

        if self._should_join(new=d):
            self._join()

        self._all.append(d)

        if isinstance(d, ToolUseAiDelta):
            tum = ToolUseMessage(ToolUse(
                id=d.id,
                name=check.not_none(d.name),
                args=d.args or {},
                raw_args=json.dumps_compact(d.args),
            ))

            for md_ty in (MessageUuid, ThoughtSignature):
                if (md := d.metadata.get(md_ty)) is not None:
                    tum = tum.with_metadata(md)

            self._out.append(tum)

        else:
            self._queue.append(d)

    def add(self, deltas: AiDeltas) -> None:
        check.state(not self._closed)

        for d in deltas:
            self._add_one(d)

    def build(self) -> AiChat:
        check.state(not self._closed)
        self._closed = True

        self._join()
        self._join_indexed_ptus()

        return list(self._out)
