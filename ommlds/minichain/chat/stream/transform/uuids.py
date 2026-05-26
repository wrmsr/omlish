import typing as ta
import uuid

from omlish import check

from ...metadata import MessageUuid
from ..types import AiDelta
from ..types import PartialToolUseAiDelta
from ..types import ToolUseAiDelta
from .types import AiDeltaTransform


##


class TypeSequentialMessageUuidAddingAiDeltaTransform(AiDeltaTransform):
    def __init__(
            self,
            uuid_factory: ta.Callable[[], uuid.UUID] = uuid.uuid4,
    ) -> None:
        super().__init__()

        self._uuid_factory = uuid_factory

        self._last: AiDelta | None = None
        self._ptus_by_index: dict[int, PartialToolUseAiDelta] = {}

    def transform(self, d: AiDelta) -> ta.Sequence[AiDelta]:
        # indexed PartialToolUseAiDeltas (handled separately)

        if isinstance(d, PartialToolUseAiDelta) and (ptu_idx := d.index) is not None:
            try:
                ptu = self._ptus_by_index[ptu_idx]

            except KeyError:
                if MessageUuid not in d.metadata:
                    d = d.with_metadata(MessageUuid(self._uuid_factory()))
                self._ptus_by_index[ptu_idx] = d

            else:
                ptu_md = ptu.metadata[MessageUuid]
                if (d_mu := d.metadata.get(MessageUuid)) is not None:
                    check.equal(d_mu, ptu_md)
                else:
                    d = d.with_metadata(ptu_md)

            return [d]

        # initial message

        last = self._last

        if last is None:
            if MessageUuid not in d.metadata:
                d = d.with_metadata(MessageUuid(self._uuid_factory()))

            self._last = d
            return [d]

        last_mu = last.metadata[MessageUuid]

        # unindexed PartialToolUseDeltas

        # FIXME: gross ugly logic dupe with joiner - make this itself joined messages, and callers know to will ignore
        #        Partials
        if (
                isinstance(last, PartialToolUseAiDelta) and
                isinstance(d, PartialToolUseAiDelta) and
                d.id is not None and
                last.id != d.id
        ):
            if (d_mu := d.metadata.get(MessageUuid)) is not None:
                check.not_equal(d_mu, last_mu)
            else:
                d = d.with_metadata(MessageUuid(self._uuid_factory()))

            self._last = d
            return [d]

        # other messages

        if MessageUuid not in d.metadata:
            if (dt := type(d)) == type(last) and dt is not ToolUseAiDelta:  # noqa
                d = d.with_metadata(last_mu)
            else:
                d = d.with_metadata(MessageUuid(self._uuid_factory()))

        self._last = d
        return [d]
