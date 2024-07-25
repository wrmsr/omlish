import typing as ta
import weakref

from .. import check
from .. import dataclasses as dc
from .. import lang


class Config(
    dc.Data,
    lang.Abstract,
    frozen=True,
    reorder=True,
    confer=frozenset([
        'frozen',
        'reorder',
        'confer',
    ]),
):
    pass


ConfigT = ta.TypeVar('ConfigT', bound='Config')

_CONFIG_CLS_MAP: ta.MutableMapping[type[Config], type['Configurable']] = weakref.WeakValueDictionary()


class Configurable(ta.Generic[ConfigT], lang.Abstract):

    # FIXME: https://github.com/python/mypy/issues/5144
    Config: ta.ClassVar[type[ConfigT]]  # type: ignore  # noqa

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        cfg_cls = check.issubclass(cls.__dict__['Config'], Config)
        check.not_in(cfg_cls, _CONFIG_CLS_MAP)
        _CONFIG_CLS_MAP[cfg_cls] = cls

    def __init__(self, config: ConfigT) -> None:
        super().__init__()

        self._config: ConfigT = check.isinstance(config, self.Config)


def get_impl(cfg: type[Config] | Config) -> type[Configurable]:
    if isinstance(cfg, type):
        cfg_cls = check.issubclass(cfg, Config)  # noqa
    elif isinstance(cfg, Config):
        cfg_cls = type(cfg)
    else:
        raise TypeError(cfg)
    return _CONFIG_CLS_MAP[cfg_cls]
