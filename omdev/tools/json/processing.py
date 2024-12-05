import dataclasses as dc
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    from omlish.specs import jmespath
else:
    jmespath = lang.proxy_import('omlish.specs.jmespath')


##


@dc.dataclass(frozen=True, kw_only=True)
class ProcessingOptions:
    jmespath_expr: ta.Any | None = None
    flat: bool = False


class Processor:
    def __init__(self, opts: ProcessingOptions) -> None:
        super().__init__()

        self._opts = opts

        jmespath_expr = opts.jmespath_expr
        if isinstance(jmespath_expr, str):
            jmespath_expr = jmespath.compile(jmespath_expr)
        self._jmespath_expr: ta.Any | None = jmespath_expr

    def process(self, v: ta.Any) -> ta.Iterable[ta.Any]:
        if self._jmespath_expr is not None:
            v = self._jmespath_expr.search(v)

        if self._opts.flat:
            if (
                    not isinstance(v, ta.Iterable) or  # noqa
                    isinstance(v, ta.Mapping) or
                    isinstance(v, lang.BUILTIN_SCALAR_ITERABLE_TYPES)
            ):
                raise TypeError(f'Flat output must be flat collections, got {type(v)}', v)

            yield from v

        else:
            yield v
