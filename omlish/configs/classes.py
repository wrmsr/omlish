import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang


ConfigurableConfigT = ta.TypeVar('ConfigurableConfigT', bound='Configurable.Config')


class Configurable(ta.Generic[ConfigurableConfigT], lang.Abstract):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config:
        """Does not use any dc metaclasses to preserve typechecking."""

        configurable_cls: ta.ClassVar[type['Configurable']]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if not lang.is_abstract_class(cls):
            check.in_('Config', cls.__dict__)
            cfg_cls = check.issubclass(cls.Config, Configurable.Config)
            check.not_in('configurable_cls', cfg_cls.__dict__)
            check.state(dc.is_immediate_dataclass(cfg_cls))
            cfg_cls.configurable_cls = cls

    def __init__(self, config: ConfigurableConfigT) -> None:
        super().__init__()

        self._config: ConfigurableConfigT = check.isinstance(config, self.Config)  # type: ignore[assignment]

    @property
    def config(self) -> ConfigurableConfigT:
        return self._config
