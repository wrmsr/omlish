"""
This module contains the core resourceful interfaces that must be implemented by any backend.
"""
import abc
import typing as ta

from ... import lang
from .columns import Columns
from .queriers import AnyQuerier
from .queriers import AsyncQuerier
from .queriers import Querier
from .rows import Row


##


class AnyRows(lang.Abstract):
    @property
    @abc.abstractmethod
    def columns(self) -> Columns:
        raise NotImplementedError


class Rows(AnyRows, ta.Iterator[Row], lang.Abstract):
    @ta.final
    def __iter__(self) -> ta.Self:
        return self

    @abc.abstractmethod
    def __next__(self) -> Row:
        raise NotImplementedError


class AsyncRows(AnyRows, ta.AsyncIterator[Row], lang.Abstract):
    @ta.final
    def __aiter__(self) -> ta.Self:
        return self

    @abc.abstractmethod
    def __anext__(self) -> ta.Awaitable[Row]:
        raise NotImplementedError


##


class AnyTransaction(AnyQuerier, lang.Abstract):
    pass


class Transaction(Querier, AnyTransaction, lang.Abstract):
    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class AsyncTransaction(AsyncQuerier, AnyTransaction, lang.Abstract):
    @abc.abstractmethod
    def commit(self) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class AnyConn(AnyQuerier, lang.Abstract):
    pass


class Conn(Querier, AnyConn, lang.Abstract):
    @abc.abstractmethod
    def begin(self) -> ta.ContextManager[Transaction]:
        raise NotImplementedError


class AsyncConn(AsyncQuerier, AnyConn, lang.Abstract):
    @abc.abstractmethod
    def begin(self) -> ta.AsyncContextManager[AsyncTransaction]:
        raise NotImplementedError


##


class AnyDb(AnyQuerier, lang.Abstract):
    pass


class Db(Querier, AnyDb, lang.Abstract):
    @abc.abstractmethod
    def connect(self) -> ta.ContextManager[Conn]:
        raise NotImplementedError


class AsyncDb(AsyncQuerier, AnyDb, lang.Abstract):
    @abc.abstractmethod
    def connect(self) -> ta.AsyncContextManager[AsyncConn]:
        raise NotImplementedError
