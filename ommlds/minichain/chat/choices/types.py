"""
TODO:
 - ChatOutputs really go on each AiChoice...
"""
import typing as ta

from omlish import lang

from ...types import Option
from ...types import Output
from ..generations import ChatGeneration
from ..types import ChatOptions
from ..types import ChatOutputs


##


class ChatChoicesOption(Option, lang.Abstract, lang.Sealed):
    pass


ChatChoicesOptions: ta.TypeAlias = ChatChoicesOption | ChatOptions


##


class ChatChoicesOutput(Output, lang.Abstract, lang.Sealed):
    pass


ChatChoicesOutputs: ta.TypeAlias = ChatChoicesOutput | ChatOutputs


##


ChatChoices: ta.TypeAlias = ta.Sequence[ChatGeneration]
