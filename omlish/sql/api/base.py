"""
TODO:
 - sync vs async
"""
import abc
import typing as ta

from ... import lang
from .columns import Column
from .columns import Columns
from .queries import Query
from .resources import ContextCloser
from .rows import Row


##


class Querier(ContextCloser, lang.Abstract):
    @property
    @abc.abstractmethod
    def adapter(self) -> 'Adapter':
        raise NotImplementedError

    @abc.abstractmethod
    def query(self, query: Query) -> 'Rows':  # ta.Raises[QueryError]
        raise NotImplementedError


##


class Rows(ContextCloser, ta.Iterator[Row], lang.Abstract):
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


class Conn(Querier, lang.Abstract):
    pass


##


class Db(Querier, lang.Abstract):
    @abc.abstractmethod
    def connect(self) -> Conn:
        raise NotImplementedError

    def query(self, query: Query) -> Rows:
        with self.connect() as conn:
            return conn.query(query)


##


class Adapter(lang.Abstract):
    @abc.abstractmethod
    def scan_type(self, c: Column) -> type:
        raise NotImplementedError
