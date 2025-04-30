import abc
import types
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..qualifiedname import QualifiedName


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


class Node(
    dc.Frozen,
    lang.Abstract,
    eq=False,
    confer=frozenset([
        *dc.get_metaclass_spec(dc.Frozen).confer,
        'eq',
    ]),
):
    @ta.final
    def __hash__(self) -> ta.NoReturn:
        raise NodeComparisonTypeError(type(self))

    @ta.final
    def __eq__(self, other) -> ta.NoReturn:
        raise NodeComparisonTypeError(type(self))

    @ta.final
    def __ne__(self, other) -> ta.NoReturn:
        raise NodeComparisonTypeError(type(self))

    @ta.final
    def __bool__(self) -> ta.NoReturn:
        raise TypeError

    #

    @dc.dataclass(frozen=True)
    class _Fields:
        cmp_fields: ta.Sequence[str]
        hash_fields: ta.Sequence[str]

    __node_fields__: ta.ClassVar[tuple[str, ...]]

    @classmethod
    def _fields(cls) -> _Fields:
        try:
            return cls.__dict__['__node_fields__']
        except KeyError:
            pass

        dc_rfl = dc.reflect(cls)
        fields = Node._Fields(
            cmp_fields=tuple(f.name for f in dc_rfl.instance_fields if f.compare),
            hash_fields=tuple(f.name for f in dc_rfl.instance_fields if (f.compare if f.hash is None else f.hash)),
        )

        setattr(cls, '__node_fields__', fields)
        return fields

    _hash: ta.ClassVar[int]

    def hash(self) -> int:
        try:
            return self._hash
        except AttributeError:
            pass

        h = hash(tuple(getattr(self, f) for f in self._fields().hash_fields))
        object.__setattr__(self, '_hash', h)
        return h

    def eq(self, other: 'Node') -> bool | types.NotImplementedType:
        if self is other:
            return True

        def rec(l, r):
            if l.__class__ is not r.__class__:
                return NotImplemented

            if isinstance(l, lang.BUILTIN_SCALAR_ITERABLE_TYPES):
                return l == r

            elif isinstance(l, ta.Mapping):
                ks = set(l)
                if set(r) != ks:
                    return False
                for k, lv in l.items():
                    rv = r[k]
                    if (ret := rec(lv, rv)) is not True:
                        return ret
                return True

            elif isinstance(l, ta.Sequence):
                if len(l) != len(r):
                    return False
                for le, re in zip(l, r):
                    if (ret := rec(le, re)) is not True:
                        return ret
                return True

            elif isinstance(l, Node):
                return l.eq(r)

            else:
                return l == r

        for f in self._fields().cmp_fields:
            lf = getattr(self, f)
            rf = getattr(other, f)
            if (ret := rec(lf, rf)) is not True:
                return ret
        return True


##


class Builder(lang.Abstract):
    pass


##


class HasQn(lang.Abstract):
    @property
    @abc.abstractmethod
    def qn(self) -> QualifiedName:
        raise NotImplementedError
