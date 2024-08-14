import enum


class JsonType(enum.Enum):
    NULL = enum.auto()
    BOOLEAN = enum.auto()
    OBJECT = enum.auto()
    ARRAY = enum.auto()
    NUMBER = enum.auto()
    STRING = enum.auto()
