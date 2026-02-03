import abc

from ... import lang
from .columns import Column


##


class Adapter(lang.Abstract):
    @abc.abstractmethod
    def scan_type(self, c: Column) -> type:
        raise NotImplementedError


##


class HasAdapter(lang.Abstract):
    @property
    @abc.abstractmethod
    def adapter(self) -> Adapter:
        raise NotImplementedError
