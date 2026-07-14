import dataclasses as dc
import typing as ta

from ..runtime import Runtime


##


@dc.dataclass(frozen=True)
class FunctionContext:
    runtime: Runtime


class Functions(ta.Protocol):
    def call_function(
            self,
            function_name: str,
            resolved_args: ta.Sequence[ta.Any],
            ctx: FunctionContext | None = None,
    ) -> ta.Any:
        ...
