import abc

from ... import lang
from ..params import ParamStyle


##


class Adapter(lang.Abstract):
    @property
    @abc.abstractmethod
    def param_style(self) -> ParamStyle | None:
        raise NotImplementedError
