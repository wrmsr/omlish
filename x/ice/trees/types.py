import typing as ta

from omnibus import dataclasses as dc
from omnibus.serde import mapping as sm

from .nodes import Node


class Query(dc.Enum, sealed=True):

    @classmethod
    def of(cls, obj: ta.Union['Query', str, Node]) -> 'Query':
        if isinstance(obj, Query):
            return obj
        elif isinstance(obj, str):
            return StrQuery(obj)
        elif isinstance(obj, Node):
            return AstQuery(obj)
        else:
            raise TypeError(obj)


class StrQuery(Query):
    src: str = dc.field(check=lambda s: isinstance(s, str) and s)


class AstQuery(Query):
    root: Node = dc.field(check=lambda o: isinstance(o, Node))


class QuerySerde(sm.AutoSerde[Query]):

    @property
    def handles_polymorphism(self) -> bool:
        return True

    def serialize(self, obj: Query) -> ta.Any:
        return sm.gen_dataclass_serde(Query, no_custom=True).serialize(obj)

    def deserialize(self, ser: ta.Any) -> Query:
        if isinstance(ser, str):
            return StrQuery(ser)
        return sm.gen_dataclass_serde(Query, no_custom=True).deserialize(ser)
