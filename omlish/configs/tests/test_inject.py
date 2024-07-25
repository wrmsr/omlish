import dataclasses as dc
import typing as ta

from ... import inject as inj
from ..classes import Configurable
from .test_classes import AThing
from .test_classes import BThing
from .test_classes import Thing


ConfigurableT = ta.TypeVar('ConfigurableT', bound=Configurable)
ConfigurableU = ta.TypeVar('ConfigurableU', bound=ConfigurableT)


@dc.dataclass(frozen=True)
class ImplFor:
    cls: type
    impl_cls: type


def bind_impl(cls: type[ConfigurableT], impl_cls: type[ConfigurableU]) -> inj.Elements:
    return inj.as_elements(
        inj.Binding(
            inj.Key(ImplFor, tag=cls, multi=True),
            inj.const(ImplFor(cls, impl_cls)),
        )
    )


def bind_factory(cls: type[Configurable]) -> inj.Elements:
    def outer(i: inj.Injector):
        def inner(config):
            raise NotImplementedError
        return inner

    fac_cls = ta.Callable[[cls.Config], cls]
    return inj.as_elements(
        inj.Binding(
            inj.Key(fac_cls),
            inj.fn(outer, fac_cls)
        ),
    )


def test_inject():
    es = inj.as_elements(
        bind_impl(Thing, AThing),
        bind_impl(Thing, BThing),
        bind_factory(Thing),
    )

    i = inj.create_injector(es)
    fac = i[inj.Key(ta.Callable[[Thing.Config], Thing])]
    print(fac)
