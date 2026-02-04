import abc

from ... import lang
from ..params import ParamStyle
from .columns import Column


##


class Adapter(lang.Abstract):
    @property
    @abc.abstractmethod
    def param_style(self) -> ParamStyle:
        raise NotImplementedError

    @abc.abstractmethod
    def scan_type(self, c: Column) -> type:
        raise NotImplementedError


##


class HasAdapter(lang.Abstract):
    @property
    @abc.abstractmethod
    def adapter(self) -> Adapter:
        raise NotImplementedError
