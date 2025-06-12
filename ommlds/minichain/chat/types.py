import typing as ta

from omlish import lang

from ..llms.types import LlmOption
from ..llms.types import LlmOutput
from ..types import Option
from ..types import Output


##


class ChatOption(Option, lang.Abstract, lang.PackageSealed):
    pass


ChatOptions: ta.TypeAlias = ChatOption | LlmOption


##


class ChatOutput(Output, lang.Abstract, lang.PackageSealed):
    pass


ChatOutputs: ta.TypeAlias = ChatOutput | LlmOutput
