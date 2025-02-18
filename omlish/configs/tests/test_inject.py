import dataclasses as dc
import typing as ta

from ... import inject as inj
from ... import lang
from ..classes import Configurable
from .test_classes import AThing
from .test_classes import BThing
from .test_classes import Thing


@dc.dataclass(frozen=True)
class ImplFor:
    cls: type
    impl_cls: type


def bind_impl(cls: type[Configurable], impl_cls: type[Configurable]) -> inj.Elements:
    if not issubclass(impl_cls, cls):
        raise TypeError(impl_cls, cls)
    inst = ImplFor(cls, impl_cls)
    return inj.as_elements(
        inj.set_binder[ImplFor](tag=cls).bind(inj.Key(ImplFor, tag=id(inst))),
        inj.bind(ImplFor, tag=id(inst), to_const=inst),
    )


ConfigT = ta.TypeVar('ConfigT', bound=Configurable.Config)
ConfigurableT = ta.TypeVar('ConfigurableT', bound=Configurable)


@dc.dataclass(frozen=True)
class Factory(ta.Generic[ConfigT, ConfigurableT]):
    fn: ta.Callable[[ConfigT], ConfigurableT]

    def __call__(self, config: ConfigT) -> ConfigurableT:
        return self.fn(config)


def bind_factory(cls: type[Configurable]) -> inj.Elements:
    def outer(i: inj.Injector):
        ifs = i.provide(inj.Key(ta.AbstractSet[ImplFor], tag=cls))
        ifd = {ic.impl_cls.Config: ic for ic in ifs}

        def inner(config):
            impl_cls = ifd[type(config)].impl_cls
            fac = lang.typed_partial(impl_cls, config=config)  # FIXME: horribly slow lol
            return i.inject(fac)

        return Factory(inner)

    fac_cls = Factory[cls.Config, cls]  # type: ignore
    return inj.as_elements(
        inj.set_binder[ImplFor](tag=cls),
        inj.bind(fac_cls, to_fn=outer, singleton=True),
    )


def test_inject():
    i = inj.create_injector(
        bind_impl(Thing, AThing),
        bind_impl(Thing, BThing),
        bind_factory(Thing),
    )
    fac: ta.Any = i[inj.Key(Factory[Thing.Config, Thing])]

    assert isinstance(fac(AThing.Config()), AThing)
    assert isinstance(fac(BThing.Config()), BThing)
