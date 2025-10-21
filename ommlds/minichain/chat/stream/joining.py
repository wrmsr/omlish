import typing as ta

from omlish import check

from ...tools.types import ToolUse
from ..choices.types import AiChoice
from ..messages import AiMessage
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

        self._choice_lsts: list[list[list[str] | ToolUse]] = []
        self._i = 0

    def _add_to(self, l: list[list[str] | ToolUse], d: AiChoiceDelta) -> None:
        if isinstance(d, ContentAiChoiceDelta):
            s = check.isinstance(d.c, str)
            if l and isinstance(l[-1], list):
                l[-1].append(s)
            else:
                l.append([s])

        elif isinstance(d, ToolUseAiChoiceDelta):
            # l.append(d.tu)
            raise NotImplementedError

        else:
            raise TypeError(d)

    def add(self, choices: ta.Sequence[AiChoiceDeltas]) -> None:
        l: list[list[str] | ToolUse]

        if self._i == 1:
            for c in choices:
                self._choice_lsts.append(l := [])
                for d in c.deltas:
                    self._add_to(l, d)

        else:
            for l, c in zip(self._choice_lsts, choices, strict=True):
                for d in c.deltas:
                    self._add_to(l, d)

    def build(self) -> list[AiChoice]:
        ret: list[AiChoice] = []

        for cl in self._choice_lsts:
            cc: list[AnyAiMessage] = []

            for e in cl:
                if isinstance(e, list):
                    cc.append(AiMessage(''.join(e)))

                elif isinstance(e, ToolUse):
                    cc.append(ToolUseMessage(e))

                else:
                    raise TypeError(e)

            ret.append(AiChoice(cc))

        return ret
