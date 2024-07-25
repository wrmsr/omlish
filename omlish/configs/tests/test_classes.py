import typing as ta

from ... import lang
from ..classes import Config
from ..classes import Configurable
from ..classes import get_impl

#


ThingConfigT = ta.TypeVar('ThingConfigT', bound='Thing.Config')


class Thing(Configurable[ThingConfigT]):
    class Config(Config, lang.Abstract):
        f: float = 0.


class AThing(Thing['AThing.Config']):
    class Config(Thing.Config):
        i: int = 1

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)


class BThing(Thing['BThing.Config']):
    class Config(Thing.Config):
        s: str = 'two'

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)


def test_configurable():
    assert get_impl(AThing.Config) is AThing
    assert get_impl(BThing.Config()) is BThing

    assert AThing()._config.i == 1  # noqa
    assert AThing(AThing.Config(i=3))._config.i == 3  # noqa


# def test_inject():
#     def install(binder: inj.Binder) -> inj.Binder:
#         cinj.bind_impl(binder, Thing, AThing)
#         cinj.bind_impl(binder, Thing, BThing)
#         cinj.bind_factory(binder, Thing)
#         return binder
#
#     binder = install(inj.create_binder())
#     injector = inj.create_injector(binder)
#     fac = injector[ta.Callable[..., Thing]]
#
#     with injector._CURRENT(injector):  # FIXME
#         thing = fac(config=AThing.Config(i=420))
#     assert isinstance(thing, AThing)
#     assert thing._config.i == 420  # noqa
#
#     with injector._CURRENT(injector):  # FIXME
#         thing = fac(config=BThing.Config(s='fourtwenty'))
#     assert isinstance(thing, BThing)  # noqa
#     assert thing._config.s == 'fourtwenty'  # noqa
