# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import functools
import typing as ta

from ...lite.check import check
from .rewriting import ConfigRewriter
from .rewriting import ConfigRewriterPath


T = ta.TypeVar('T')


##


class MatchingConfigRewriter(ConfigRewriter):
    def __init__(
            self,
            fn: ta.Callable[[ta.Any], ta.Any],
            paths: ta.Iterable[ConfigRewriterPath],
            *,
            recurse: bool = False,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._paths = frozenset(check.isinstance(p, tuple) for p in paths)
        self._recurse = recurse

    def rewrite(self, ctx: ConfigRewriter.Context[T]) -> T:
        if ctx.path in self._paths:
            no = self._fn(ctx.obj)
            if not self._recurse:
                return no
            ctx = dc.replace(ctx, obj=no)

        return super().rewrite(ctx)


def matched_config_rewrite(
        fn: ta.Callable[[ta.Any], ta.Any],
        obj: T,
        *paths: ConfigRewriterPath,
        recurse: bool = False,
        **kwargs: ta.Any,
) -> T:
    return MatchingConfigRewriter(
        functools.partial(fn, **kwargs),
        paths,
        recurse=recurse,
    )(obj)
