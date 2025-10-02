import dataclasses as dc
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    from omlish import marshal as msh
    from omlish.specs import jmespath
else:
    msh = lang.proxy_import('omlish.marshal')
    jmespath = lang.proxy_import('omlish.specs.jmespath')


##


@dc.dataclass(frozen=True, kw_only=True)
class ProcessingOptions:
    jmespath_expr: ta.Any | None = None
    marshal: bool = False
    flat: bool = False
    prune_empty: bool = False
    omit_empty: bool = False


def _prune_empty(v: ta.Any) -> ta.Any:
    # if isinstance(v, ta.Mapping):
    #     v = type(v)([
    #         (_prune_empty(k), _prune_empty(v))
    #         for k, v in v.items()
    #     ])
    # elif
    raise NotImplementedError


class Processor:
    def __init__(self, opts: ProcessingOptions) -> None:
        super().__init__()

        self._opts = opts

        jmespath_expr = opts.jmespath_expr
        if isinstance(jmespath_expr, str):
            jmespath_expr = jmespath.compile(jmespath_expr)
        self._jmespath_expr: ta.Any | None = jmespath_expr

    @lang.cached_function
    def _marshaler_factory(self) -> 'msh.MarshalerFactory':
        return msh.new_standard_marshaler_factory(
            first=[msh.BASE64_MARSHALER_FACTORY],
        )

    def _marshal(self, v: ta.Any) -> ta.Any:
        return msh.MarshalContext(
            configs=msh.global_config_registry(),
            marshal_factory_context=msh.MarshalFactoryContext(
                configs=msh.global_config_registry(),
                marshaler_factory=self._marshaler_factory(),
            ),
        ).marshal(v)

    def process(self, v: ta.Any) -> ta.Iterator[ta.Any]:
        if self._jmespath_expr is not None:
            v = self._jmespath_expr.search(v)

        if self._opts.marshal:
            v = self._marshal(v)

        vs: ta.Iterable[ta.Any]
        if self._opts.flat:
            if (
                    not isinstance(v, ta.Iterable) or  # noqa
                    isinstance(v, ta.Mapping) or
                    isinstance(v, lang.BUILTIN_SCALAR_ITERABLE_TYPES)
            ):
                raise TypeError(f'Flat output must be flat collections, got {type(v)}', v)

            vs = v

        else:
            vs = [v]

        for v in vs:
            if self._opts.prune_empty:
                v = _prune_empty(v)

            if self._opts.omit_empty:
                if v is None or (isinstance(v, (ta.Sequence, ta.Mapping)) and not v):
                    continue

            yield v
