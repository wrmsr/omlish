"""
This module contains the core resourceful interfaces that must be implemented by any backend.
"""
import abc
import typing as ta

from ... import lang
from .columns import Columns
from .queriers import Querier
from .rows import Row


##


class Rows(ta.Iterator[Row], lang.Abstract):
    @property
    @abc.abstractmethod
    def columns(self) -> Columns:
        raise NotImplementedError

    @ta.final
    def __iter__(self) -> ta.Self:
        return self

    @abc.abstractmethod
    def __next__(self) -> Row:  # ta.Raises[StopIteration]
        raise NotImplementedError


##


class Transaction(Querier, lang.Abstract):
    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


##


class Conn(Querier, lang.Abstract):
    @abc.abstractmethod
    def begin(self) -> ta.ContextManager[Transaction]:
        raise NotImplementedError


##


class Db(Querier, lang.Abstract):
    @abc.abstractmethod
    def connect(self) -> ta.ContextManager[Conn]:
        raise NotImplementedError
