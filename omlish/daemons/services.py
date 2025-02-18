import abc
import typing as ta

from .. import check
from .. import lang
from ..configs.classes import Configurable


ServiceConfigT = ta.TypeVar('ServiceConfigT', bound='Service.Config')


##


class Service(Configurable[ServiceConfigT], lang.Abstract):
    class Config(Configurable.Config):
        pass

    #

    @classmethod
    def from_config(cls, config: Config) -> 'Service':
        return check.isinstance(config.configurable_cls(config), cls)

    #

    @abc.abstractmethod
    def _run(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        self._run()

    @classmethod
    def run_config(cls, config: Config) -> None:
        return cls.from_config(config).run()
