import typing as ta

from ... import lang
from .. import classes as cl


#


ThingConfigT = ta.TypeVar('ThingConfigT', bound='Thing.Config')


class Thing(cl.Configurable[ThingConfigT]):
    class Config(cl.Config, lang.Abstract):
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
    assert cl.get_impl(AThing.Config) is AThing
    assert cl.get_impl(BThing.Config()) is BThing

    assert AThing()._config.i == 1  # noqa
    assert AThing(AThing.Config(i=3))._config.i == 3  # noqa
