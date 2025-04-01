import typing as ta

from ... import dataclasses as dc
from ... import lang


##


Value: ta.TypeAlias = ta.Any


##


class NodeComparisonTypeError(TypeError):
    def __init__(self, cls: type['Node'], *args: ta.Any) -> None:
        super().__init__(
            'Query node types are not comparable or hashable - this would be a common source of confusion when '
            'constructing query filters',
            cls,
            *args,
        )


class Node(dc.Frozen, lang.Abstract, cache_hash=True, eq=False):
    __compare_fields__: ta.ClassVar[tuple[str, ...]]

    @classmethod
    def _compare_fields(cls) -> tuple[str, ...]:
        try:
            return cls.__dict__['__compare_fields__']
        except KeyError:
            pass
        dc_info = dc.reflect(cls)
        cmp_fields = tuple(field.name for field in dc_info.instance_fields if field.compare)
        setattr(cls, '__compare_fields__', cmp_fields)
        return cmp_fields

    def __hash__(self) -> ta.NoReturn:
        raise NodeComparisonTypeError(type(self))

    def __eq__(self, other) -> ta.NoReturn:
        raise NodeComparisonTypeError(type(self))

    def __ne__(self, other) -> ta.NoReturn:
        raise NodeComparisonTypeError(type(self))

    _hash: ta.ClassVar[int]

    def hash(self) -> int:
        try:
            return self._hash
        except AttributeError:
            pass
        raise NotImplementedError

    def eq(self, other: 'Node') -> bool:
        raise NotImplementedError


class Builder(lang.Abstract):
    pass
