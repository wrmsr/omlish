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
    return inj.as_elements(
        inj.Binding(
            inj.Key(ImplFor, tag=cls, multi=True),
            inj.const((ImplFor(cls, impl_cls),)),
        ),
    )


def bind_factory(cls: type[Configurable]) -> inj.Elements:
    def outer(i: inj.Injector):
        ifs = i.provide(inj.Key(ImplFor, tag=cls, multi=True))
        ifd = {ic.impl_cls.Config: ic for ic in ifs}

        def inner(config):
            impl_cls = ifd[type(config)].impl_cls
            fac = lang.typed_partial(impl_cls, config=config)  # FIXME: horribly slow lol
            return i.inject(fac)

        return inner

    fac_cls = ta.Callable[[cls.Config], cls]  # type: ignore
    return inj.as_elements(
        inj.singleton(inj.Binding(
            inj.Key(fac_cls),  # type: ignore
            inj.fn(outer, fac_cls),  # type: ignore
        )),
    )


def test_inject():
    es = inj.as_elements(
        bind_impl(Thing, AThing),
        bind_impl(Thing, BThing),
        bind_factory(Thing),
    )

    i = inj.create_injector(es)
    fac: ta.Any = i[inj.Key(ta.Callable[[Thing.Config], Thing])]  # type: ignore

    assert isinstance(fac(AThing.Config()), AThing)
    assert isinstance(fac(BThing.Config()), BThing)
