import typing as ta

from .. import classes as cl
from .. import configs as cfgs
from .. import inject as cinj
from ... import dataclasses as dc
from ... import inject as inj


ThingConfigT = ta.TypeVar('ThingConfigT', bound='Thing.Config')


class Thing(cl.Configurable[ThingConfigT]):
    class Config(cfgs.Config, abstract=True):
        f: float = dc.field(0., check_type=float)


class AThing(Thing['AThing.Config']):
    class Config(Thing.Config):
        i: int = dc.field(1, check_type=int)

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)


class BThing(Thing['BThing.Config']):
    class Config(Thing.Config):
        s: str = dc.field('two', check_type=str)

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)


def test_configurable():
    assert cl.get_impl(AThing.Config) is AThing
    assert cl.get_impl(BThing.Config()) is BThing

    assert AThing()._config.i == 1
    assert AThing(AThing.Config(i=3))._config.i == 3


def test_inject():
    def install(binder: inj.Binder) -> inj.Binder:
        cinj.bind_impl(binder, Thing, AThing)
        cinj.bind_impl(binder, Thing, BThing)
        cinj.bind_factory(binder, Thing)
        return binder

    binder = install(inj.create_binder())
    injector = inj.create_injector(binder)
    fac = injector[ta.Callable[..., Thing]]

    with injector._CURRENT(injector):  # FIXME
        thing = fac(config=AThing.Config(i=420))
    assert isinstance(thing, AThing)
    assert thing._config.i == 420

    with injector._CURRENT(injector):  # FIXME
        thing = fac(config=BThing.Config(s='fourtwenty'))
    assert isinstance(thing, BThing)
    assert thing._config.s == 'fourtwenty'
