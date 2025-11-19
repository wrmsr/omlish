import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ....stream.services import StreamOptions
from ....types import Option
from ....types import Output
from ...stream.types import AiDeltas
from ..types import ChatChoicesOptions


##


class ChatChoicesStreamOption(Option, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesStreamOptions: ta.TypeAlias = ChatChoicesStreamOption | StreamOptions | ChatChoicesOptions


##


class ChatChoicesStreamOutput(Output, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesStreamOutputs: ta.TypeAlias = ChatChoicesStreamOutput


##


@dc.dataclass(frozen=True)
class AiChoiceDeltas(lang.Final):
    deltas: AiDeltas


@dc.dataclass(frozen=True)
class AiChoicesDeltas(lang.Final):
    choices: ta.Sequence[AiChoiceDeltas]
