import inspect
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import inject as inj
from .. import lang
from .. import reflect as rfl
from .classes import Configurable
from .classes import get_impl
from .configs import Config


class _UNDERLYING(lang.Marker):
    pass


def bind_impl(binder: inj.Binder, cls: ta.Type[Configurable], impl_cls: ta.Type[Configurable]) -> None:
    check.isinstance(binder, inj.Binder)
    check.issubclass(cls, Configurable)
    check.issubclass(impl_cls, cls)

    impl_assists = {'config'}
    provider_kwargs = {
        '__factory': inj.Key(ta.Callable[..., impl_cls], _UNDERLYING),
    }

    init_defaults = {
        p.name: p.default
        for p in inspect.signature(impl_cls.__init__).parameters.values()
        if p.default is not inspect.Signature.empty
    }

    if dc.is_dataclass(impl_cls.Config):
        for f in dc.fields(impl_cls.Config):
            fty = rfl.unpack_optional(f.type) or f.type

            if isinstance(fty, type) and issubclass(fty, Config):
                check.not_in(f.name, impl_assists)
                check.not_in(f.name, provider_kwargs)
                impl_assists.add(f.name)
                # FIXME: forward anns
                provider_kwargs[f.name] = inj.Key(ta.Callable[..., get_impl(fty)])

    @inj.annotate(factory=_UNDERLYING)
    def provide(config, __factory, **kwargs) -> impl_cls:
        fac_kwargs = {
            k: v(config=cfg) if cfg is not None else init_defaults[k]
            for k, v in kwargs.items()
            for cfg in [getattr(config, k)]
        }
        return __factory(config=config, **fac_kwargs)

    binder.bind_class(impl_cls, key=inj.Key(impl_cls, _UNDERLYING), assists=impl_assists)
    binder.bind_callable(provide, assists={'config'}, kwargs=provider_kwargs)

    binder.new_dict_binder(ta.Type[cls.Config], ta.Callable[..., cls]).bind(impl_cls.Config, to_provider=ta.Callable[..., impl_cls])  # noqa


def bind_dict(binder: inj.Binder, cls: ta.Type[Configurable]) -> None:
    check.isinstance(binder, inj.Binder)
    check.issubclass(cls, Configurable)

    binder.new_dict_binder(ta.Type[cls.Config], ta.Callable[..., cls])


def bind_factory(binder: inj.Binder, cls: ta.Type[Configurable]) -> None:
    check.isinstance(binder, inj.Binder)
    check.issubclass(cls, Configurable)

    bind_dict(binder, cls)

    def provide(
            config: cls.Config,
            facs: ta.Mapping[ta.Type[cls.Config], ta.Callable[..., cls]],
    ) -> cls:
        fac = facs[type(config)]
        return fac(config=config)

    binder.bind_callable(provide, assists={'config'})
