import abc

from ... import lang
from .ast import Node


##


class ExpRef(lang.Abstract):
    @property
    @abc.abstractmethod
    def expression(self) -> Node:
        raise NotImplementedError
