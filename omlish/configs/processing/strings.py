# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - env vars
 - coalescing - {$FOO|$BAR|baz}
 - minja?
"""
import typing as ta

from .rewriting import ConfigRewriter


T = ta.TypeVar('T')
StrT = ta.TypeVar('StrT', bound=str)


##


class StringConfigRewriter(ConfigRewriter):
    def __init__(
            self,
            fn: ta.Optional[ta.Callable[[str], str]] = None,
    ) -> None:
        super().__init__()

        self._fn = fn

    def rewrite_str(self, ctx: ConfigRewriter.Context[StrT]) -> StrT:
        v = ctx.obj
        if (fn := self._fn) is not None:
            if not ctx.raw:
                v = fn(v)  # type: ignore
        return type(v)(v)


##


def format_config_strings(v: T, rpl: ta.Mapping[str, str]) -> T:
    def fn(v):
        return v.format(**rpl)

    return StringConfigRewriter(fn)(v)
