"""
TODO:
 - ChatOutputs really go on each AiChoice...
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ...types import Option
from ...types import Output
from ..messages import AnyAiMessage
from ..types import ChatOptions
from ..types import ChatOutputs


##


class ChatChoicesOption(Option, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesOptions: ta.TypeAlias = ChatChoicesOption | ChatOptions


##


class ChatChoicesOutput(Output, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesOutputs: ta.TypeAlias = ChatChoicesOutput | ChatOutputs


##


@dc.dataclass(frozen=True)
class AiChoice(lang.Final):
    m: AnyAiMessage


AiChoices: ta.TypeAlias = ta.Sequence[AiChoice]
