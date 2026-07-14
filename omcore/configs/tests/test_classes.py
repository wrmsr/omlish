import dataclasses as dc
import typing as ta

from ... import lang
from .. import classes as cl


#


ThingConfigT = ta.TypeVar('ThingConfigT', bound='Thing.Config')


class Thing(cl.Configurable[ThingConfigT]):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config(cl.Configurable.Config, lang.Abstract):
        f: float = 0.


class AThing(Thing['AThing.Config']):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config(Thing.Config):
        i: int = 1

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)


class BThing(Thing['BThing.Config']):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config(Thing.Config):
        s: str = 'two'

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)


def test_configurable():
    assert AThing.Config.configurable_cls is AThing
    assert BThing.Config.configurable_cls is BThing

    assert AThing()._config.i == 1  # noqa
    assert AThing(AThing.Config(i=3))._config.i == 3  # noqa
