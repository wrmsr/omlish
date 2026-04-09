import typing as ta
import uuid

from omlish import check

from ...metadata import MessageUuid
from ..types import AiDelta
from ..types import PartialToolUseAiDelta
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

    def transform(self, d: AiDelta) -> ta.Sequence[AiDelta]:
        last = self._last

        if last is None:
            if MessageUuid not in d.metadata:
                d = d.with_metadata(MessageUuid(self._uuid_factory()))

            self._last = d
            return [d]

        last_mu = last.metadata[MessageUuid]

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

        if MessageUuid not in d.metadata:
            if type(d) == type(last):  # noqa
                d = d.with_metadata(last_mu)
            else:
                d = d.with_metadata(MessageUuid(self._uuid_factory()))

        self._last = d
        return [d]
