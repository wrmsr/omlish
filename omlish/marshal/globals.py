import threading
import typing as ta

from .. import check
from .. import lang
from .api.configs import Config
from .api.configs import ConfigRegistry
from .api.options import Option
from .api.types import MarshalerFactory
from .api.types import Marshaling
from .api.types import UnmarshalerFactory
from .api.values import Value
from .factories.api import LazyInit
from .factories.api import LazyInitFn
from .factories.api import ModuleImport
from .standard.api import StandardMarshalerFactories
from .standard.api import StandardUnmarshalerFactories
from .standard.default import DEFAULT_STANDARD_FACTORIES


if ta.TYPE_CHECKING:
    from .standard import factories as _sf
else:
    _sf = lang.proxy_import('.standard.factories', __package__)


T = ta.TypeVar('T')


##


_GLOBAL_LOCK = threading.RLock()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_config_registry() -> ConfigRegistry:
    return ConfigRegistry(lock=_GLOBAL_LOCK)


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_marshaler_factory() -> MarshalerFactory:
    return _sf.new_standard_marshaler_factory()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_unmarshaler_factory() -> UnmarshalerFactory:
    return _sf.new_standard_unmarshaler_factory()


class _GlobalMarshaling(Marshaling, lang.Final):
    def get_config_registry(self) -> ConfigRegistry:
        return global_config_registry()

    def get_marshaler_factory(self) -> MarshalerFactory:
        return global_marshaler_factory()

    def get_unmarshaler_factory(self) -> UnmarshalerFactory:
        return global_unmarshaler_factory()


@lang.cached_function(lock=_GLOBAL_LOCK)
def global_marshaling() -> Marshaling:
    return _GlobalMarshaling()


##


def marshal(
        obj: ta.Any,
        ty: ta.Any | None = None,
        *options: Option,
) -> Value:
    return global_marshaling().marshal(obj, ty, *options)


@ta.overload
def unmarshal(
        v: Value,
        ty: type[T],
        *options: Option,
) -> T:
    ...


@ta.overload
def unmarshal(
        v: Value,
        ty: ta.Any,
        *options: Option,
) -> ta.Any:
    ...


def unmarshal(v, ty, *options):
    return global_marshaling().unmarshal(v, ty, *options)


##


def register_global_config(
        key: ta.Any,
        *items: Config,
        identity: bool = False,
) -> None:
    global_config_registry().register(
        key,
        *items,
        identity=identity,
    )


def register_global_lazy_init(
        fn: LazyInitFn,
) -> None:
    global_config_registry().register(
        None,
        LazyInit(fn),
    )


def register_global_module_import(
        name: str,
        package: str | None = None,
) -> None:
    global_config_registry().register(
        None,
        LazyInit(ModuleImport(name, package)),
    )


##


def install_standard_factories(
        *factories: MarshalerFactory | UnmarshalerFactory,
) -> None:
    install_standard_factories_to(
        global_config_registry(),
        *factories,
    )


def install_standard_factories_to(
        cfgs: ConfigRegistry,
        *factories: MarshalerFactory | UnmarshalerFactory,
) -> None:
    with cfgs._lock:  # noqa
        m_cfg = check.opt_single(cfgs.get_of(None, StandardMarshalerFactories))
        u_cfg = check.opt_single(cfgs.get_of(None, StandardUnmarshalerFactories))

        m_lst: list[MarshalerFactory] = list(
            m_cfg.lst if m_cfg is not None else DEFAULT_STANDARD_FACTORIES.marshaler_factories,
        )
        u_lst: list[UnmarshalerFactory] = list(
            u_cfg.lst if u_cfg is not None else DEFAULT_STANDARD_FACTORIES.unmarshaler_factories,
        )

        m_new = False
        u_new = False

        for f in factories:
            k = False

            if isinstance(f, MarshalerFactory):
                m_lst[0:0] = [f]
                m_new = True
                k = True

            if isinstance(f, UnmarshalerFactory):
                u_lst[0:0] = [f]
                u_new = True
                k = True

            if not k:
                raise TypeError(f)

        if m_new:
            cfgs.register(None, StandardMarshalerFactories(m_lst), replace=True)
        if u_new:
            cfgs.register(None, StandardUnmarshalerFactories(u_lst), replace=True)
