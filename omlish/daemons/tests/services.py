import abc
import dataclasses as dc
import time
import typing as ta

from omlish import check
from omlish import lang


ServiceConfigT = ta.TypeVar('ServiceConfigT', bound='Service.Config')


##


class Service(lang.Abstract, ta.Generic[ServiceConfigT]):
    @dc.dataclass(frozen=True)
    class Config:
        service_cls: ta.ClassVar[type['Service']]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if not lang.is_abstract_class(cls):
            check.in_('Config', cls.__dict__)
            cfg_cls = check.issubclass(cls.Config, Service.Config)
            check.not_in('service_cls', cfg_cls.__dict__)
            cfg_cls.service_cls = cls

    #

    def __init__(self, config: ServiceConfigT) -> None:
        super().__init__()

        self._config: ServiceConfigT = check.isinstance(config, self.Config)  # type: ignore[assignment]

    #

    @abc.abstractmethod
    def _run(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        self._run()


##


class HiService(Service['HiService.Config']):
    class Config(Service.Config):
        num_reps: int = 10
        rep_sleep_s: float = .1

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    def _run(self) -> None:
        for i in range(self._config.num_reps):
            print(i)
            time.sleep(self._config.rep_sleep_s)


##


def _main() -> None:
    hi_cfg = HiService.Config()
    hi = HiService(hi_cfg)
    hi.run()


if __name__ == '__main__':
    _main()
