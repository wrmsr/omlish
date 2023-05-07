import typing as ta
import weakref

from .. import check
from .. import lang
from .configs import Config


ConfigT = ta.TypeVar('ConfigT', bound='Config')


_CFG_CLS_MAP: ta.MutableMapping[ta.Type['Config'], ta.Type['Configurable']] = weakref.WeakValueDictionary()


class Configurable(ta.Generic[ConfigT], lang.Abstract):

    Config: ta.ClassVar[ta.Type[ConfigT]]

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        cfg_cls = check.issubclass(cls.__dict__['Config'], Config)
        check.not_in(cfg_cls, _CFG_CLS_MAP)
        _CFG_CLS_MAP[cfg_cls] = cls

    def __init__(self, config: ConfigT) -> None:
        super().__init__()

        self._config: ConfigT = check.isinstance(config, self.Config)


def get_impl(cfg: ta.Union[ta.Type[Config], Config]) -> ta.Type[Configurable]:
    if isinstance(cfg, type):
        cfg_cls = check.issubclass(cfg, Config)
    elif isinstance(cfg, Config):
        cfg_cls = type(cfg)
    else:
        raise TypeError(cfg)
    return _CFG_CLS_MAP[cfg_cls]
