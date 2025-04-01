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
from .rows import Row


##


class Closer(lang.Abstract):
    def close(self) -> None:
        pass


class ContextCloser(Closer):
    def __enter__(self) -> ta.Self:
        return self

    @ta.final
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


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


class Rows(ContextCloser, lang.Abstract):
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


class Conn(Querier, lang.Abstract):  # noqa
    pass


##


class Db(Querier, lang.Abstract):  # noqa
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
