import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang
from omcore import typedvalues as tv

from ..._typedvalues import _tv_field_metadata
from ...llms.types import LlmOutput
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


ChatChoicesOutputs: ta.TypeAlias = ChatChoicesOutput | LlmOutput


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
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
