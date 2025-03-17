import enum
import typing as ta

from ... import dataclasses as dc


##


class SimpleType(enum.Enum):
    DOUBLE = 'double'
    FLOAT = 'float'
    INT32 = 'int32'
    INT64 = 'int64'
    UINT32 = 'uint32'
    UINT64 = 'uint64'
    SINT32 = 'sint32'
    SINT64 = 'sint64'
    FIXED32 = 'fixed32'
    FIXED64 = 'fixed64'
    SFIXED32 = 'sfixed32'
    SFIXED64 = 'sfixed64'
    BOOL = 'bool'
    STRING = 'string'
    BYTES = 'bytes'


class TypeRef(dc.Frozen):
    name: str


Type: ta.TypeAlias = SimpleType | TypeRef


##


class Field(dc.Frozen):
    name: str
    type: Type
    num: int
    repeated: bool = False


class Message(dc.Frozen):
    name: str
    fields: ta.Sequence[Field]


##


class ProtoFile(dc.Frozen):
    messages: ta.Sequence[Message] | None = None
