import enum
import typing as ta


class JsonType(enum.Enum):
    NULL = enum.auto()
    BOOLEAN = enum.auto()
    OBJECT = enum.auto()
    ARRAY = enum.auto()
    NUMBER = enum.auto()
    STRING = enum.auto()


TYPE_SETS_BY_JSON_TYPE: ta.Mapping[JsonType, ta.AbstractSet[type]] = {
    JsonType.NULL: {type(None)},
    JsonType.BOOLEAN: {bool},
    JsonType.OBJECT: {dict},
    JsonType.ARRAY: {list},
    JsonType.NUMBER: {int, float},
    JsonType.STRING: {str},
}
