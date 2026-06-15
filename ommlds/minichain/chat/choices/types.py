import typing as ta

from omlish import check
from omlish import typedvalues as tv
from omlish import dataclasses as dc
from omlish import lang

from ..._typedvalues import _tv_field_metadata
from ...types import Option
from ...types import Output
from ..generations import ChatGeneration
from ..types import ChatOptions


##


class ChatChoicesOption(Option, lang.Abstract, lang.Sealed):
    pass


ChatChoicesOptions: ta.TypeAlias = ChatChoicesOption | ChatOptions


##


class ChatChoicesOutput(Output, lang.Abstract, lang.Sealed):
    pass


ChatChoicesOutputs: ta.TypeAlias = ChatChoicesOutput


##


@dc.dataclass(frozen=True)
class ChatChoices(lang.Final):
    gs: ta.Sequence[ChatGeneration]

    #

    _outputs: ta.Sequence[ChatChoicesOutputs] = dc.field(
        default=(),
        metadata=_tv_field_metadata(
            ChatChoicesOutputs,
            marshal_name='outputs',
        ),
    )

    @property
    def outputs(self) -> tv.TypedValues[ChatChoicesOutputs]:
        return check.isinstance(self._outputs, tv.TypedValues)
