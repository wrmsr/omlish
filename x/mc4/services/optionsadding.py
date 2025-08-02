import dataclasses as dc
import typing as ta

from ommlds import minichain as mc


RequestV = ta.TypeVar('RequestV')
OptionT = ta.TypeVar('OptionT', bound=mc.Option)
ResponseV = ta.TypeVar('ResponseV')
OutputT = ta.TypeVar('OutputT', bound=mc.Output)


##


@dc.dataclass(frozen=True)
class OptionsAddingService(ta.Generic[RequestV, OptionT, ResponseV, OutputT]):
    inner: mc.Service[mc.Request[RequestV, OptionT], mc.Response[ResponseV, OutputT]]
    options: ta.Sequence[OptionT]
    override: bool = dc.field(default=False, kw_only=True)

    def invoke(self, request: mc.Request[RequestV, OptionT]) -> mc.Response[ResponseV, OutputT]:
        return self.inner.invoke(request.with_options(*self.options, override=self.override))
