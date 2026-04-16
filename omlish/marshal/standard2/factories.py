import abc
import typing as ta

from ... import check
from ... import reflect as rfl
from ..api.configs import ConfigRegistry
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.registries import Registry
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..factories.lazyinit.factories import LazyInitRunningMarshalerFactory
from ..factories.lazyinit.factories import LazyInitRunningUnmarshalerFactory
from ..factories.multi import MultiMarshalerFactory
from ..factories.multi import MultiUnmarshalerFactory
from ..factories.recursive import RecursiveMarshalerFactory
from ..factories.recursive import RecursiveUnmarshalerFactory
from ..factories.typecache import TypeCacheMarshalerFactory
from ..factories.typecache import TypeCacheUnmarshalerFactory
from .api import StandardMarshalerFactories
from .api import StandardUnmarshalerFactories
from .default import DEFAULT_STANDARD_FACTORIES


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)
FactoriesT = ta.TypeVar('FactoriesT', bound=StandardMarshalerFactories | StandardUnmarshalerFactories)


##


class _StandardFactory(ta.Generic[FactoryT, FactoriesT]):
    def __init__(
            self,
            *,
            first: ta.Iterable[FactoryT] | None = None,
            last: ta.Iterable[FactoryT] | None = None,
    ) -> None:
        super().__init__()

        self._first = tuple(first or ())
        self._last = tuple(last or ())

        self._state: tuple[FactoriesT, FactoryT] | None = None

    _cfg_cls: ta.ClassVar[type[FactoriesT]]  # noqa
    _default_facs: ta.ClassVar[ta.Sequence[FactoryT]]  # noqa

    def _get_fac(self, cfgs: ConfigRegistry) -> FactoryT:
        st: ta.Any = self._state
        cfg: ta.Any = check.opt_single(cfgs.get_of(None, self._cfg_cls))
        if st is not None and cfg is not None and st[0] is cfg:
            return st[1]

        with cfgs._lock:  # noqa
            st = self._state
            cfg = check.opt_single(cfgs.get_of(None, self._cfg_cls))
            if st is not None and cfg is not None and st[0] is cfg:
                return st[1]

            if cfg is None:
                cfg = self._cfg_cls(self._default_facs)  # type: ignore[arg-type]
                cfgs.register(None, cfg)

            fac = self._make_fac(cfgs, cfg)

            st = (cfg, fac)
            self._state = st

            return fac

    @abc.abstractmethod
    def _make_fac(self, cfgs: ConfigRegistry, cfg: FactoriesT) -> FactoryT:
        raise NotImplementedError


class StandardMarshalerFactory(_StandardFactory[MarshalerFactory, StandardMarshalerFactories], MarshalerFactory):
    _cfg_cls = StandardMarshalerFactories
    _default_facs = DEFAULT_STANDARD_FACTORIES.marshaler_factories

    def _make_fac(self, cfgs: ConfigRegistry, cfg: StandardMarshalerFactories) -> MarshalerFactory:
        fac: MarshalerFactory = MultiMarshalerFactory(
            *self._first,
            *cfg.lst,
            *self._last,
        )

        fac = RecursiveMarshalerFactory(fac)
        fac = TypeCacheMarshalerFactory(fac)
        fac = LazyInitRunningMarshalerFactory(fac)

        return fac

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        return self._get_fac(check.isinstance(ctx.configs, Registry)).make_marshaler(ctx, rty)


class StandardUnmarshalerFactory(_StandardFactory[UnmarshalerFactory, StandardUnmarshalerFactories], UnmarshalerFactory):  # noqa
    _cfg_cls = StandardUnmarshalerFactories
    _default_facs = DEFAULT_STANDARD_FACTORIES.unmarshaler_factories

    def _make_fac(self, cfgs: ConfigRegistry, cfg: StandardUnmarshalerFactories) -> UnmarshalerFactory:
        fac: UnmarshalerFactory = MultiUnmarshalerFactory(
            *self._first,
            *cfg.lst,
            *self._last,
        )

        fac = RecursiveUnmarshalerFactory(fac)
        fac = TypeCacheUnmarshalerFactory(fac)
        fac = LazyInitRunningUnmarshalerFactory(fac)

        return fac

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        return self._get_fac(check.isinstance(ctx.configs, Registry)).make_unmarshaler(ctx, rty)
