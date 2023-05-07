"""
TODO:
 - SingletonEnum? - java-style inner classes are all singletons - could tools understand shared parent inheritance?
 - inheritance>
 - IntEnum/Flag from base

TODO:

@functools.total_ordering
class OrderedEnum(enum.Enum):
    __member_indexes__: ta.ClassVar[ta.Mapping[ta.Any, int]]
    def __lt__(self, other):
        if type(self) is not type(self):
            return NotImplemented
        try:
            mi = type(self).__dict__['__member_indexes__']
        except KeyError:
            mi = {v: i for i, v in enumerate(type(self))}
            setattr(type(self), '__member_indexes__', mi)
        return mi[self] < mi[other]

@functools.total_ordering
class ValueOrderedEnum(Enum):
    def __lt__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.value < other.value
"""
import enum
import typing as ta

from .classes import SimpleMetaDict
from .strings import is_dunder


EnumT = ta.TypeVar('EnumT', bound=enum.Enum)
V = ta.TypeVar('V')


_EnumDict = enum._EnumDict  # type: ignore


def parse_enum(obj: ta.Union[EnumT, str], cls: ta.Type[EnumT]) -> EnumT:
    if isinstance(obj, cls):
        return ta.cast(EnumT, cls)
    elif not isinstance(obj, str) or obj.startswith('__'):
        raise ValueError(f'Illegal {cls!r} name: {obj!r}')
    else:
        return getattr(cls, obj)


class _AutoEnumMeta(enum.EnumMeta):

    class Dict(SimpleMetaDict, _EnumDict):  # type: ignore

        def __init__(self, src: _EnumDict) -> None:  # type: ignore
            super().__init__()
            if hasattr(src, '_cls_name'):  # 3.9
                self._cls_name = src._cls_name  # type: ignore
            self.update(src)
            if hasattr(src, '_generate_next_value'):  # 3.8
                self._generate_next_value = src._generate_next_value  # type: ignore

        def __setitem__(self, key, value):
            if value is Ellipsis:
                value = enum.auto()
            return super().__setitem__(key, value)

    def __new__(mcls, name, bases, namespace):
        if 'AutoEnum' not in globals():
            return type.__new__(mcls, name, bases, namespace)
        bases = tuple(b if b is not AutoEnum else enum.Enum for b in bases)
        return super().__new__(mcls, name, bases, namespace)

    @classmethod
    def __prepare__(mcls, cls, bases):
        if 'AutoEnum' not in globals():
            return {}
        bases = tuple(b if b is not AutoEnum else enum.Enum for b in bases)
        return _AutoEnumMeta.Dict(super().__prepare__(cls, bases))


class AutoEnum(metaclass=_AutoEnumMeta):
    pass


class _ValueEnumMeta(type):

    IGNORED_BASES = {
        object,
        ta.Generic,
    }

    ILLEGAL_ATTRS = {
        '__members__',
        '__members_by_name__',
        '__members_by_value__',
    }

    def __iter__(cls) -> ta.Iterator[str]:
        return iter(cls.__members_by_name__)

    class _ByValueDescriptor:

        def __get__(self, instance, owner=None):
            if owner is None:
                return self

            by_value = {}
            for k, v in owner.__members_by_name__.items():
                if v in by_value:
                    raise TypeError(f'Duplicate value {v!r} with name {k!r}')
                by_value[v] = k

            owner.__members_by_value__ = by_value
            return by_value

    def __new__(mcls, name, bases, namespace, *, unique=False, ignore=(), **kwargs):
        if isinstance(ignore, str):
            raise TypeError(ignore)

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)  # noqa

        for k in mcls.ILLEGAL_ATTRS:
            if k in namespace:
                raise NameError(k)

        pairs = []
        by_name = {}
        for mrocls in cls.__mro__:
            if mrocls in mcls.IGNORED_BASES:
                continue
            for k, v in mrocls.__dict__.items():
                if k in mcls.ILLEGAL_ATTRS or k in ignore or is_dunder(k):
                    continue
                pairs.append((k, v))
                if k not in by_name:
                    by_name[k] = v

        cls.__members__ = pairs
        cls.__members_by_name__ = by_name
        cls.__members_by_value__ = mcls._ByValueDescriptor()  # noqa

        if unique:
            getattr(cls, '__members_by_value__')

        return cls


class ValueEnum(ta.Generic[V], metaclass=_ValueEnumMeta):

    __members__: ta.ClassVar[ta.Sequence[ta.Tuple[str, V]]]
    __members_by_name__: ta.ClassVar[ta.Mapping[str, V]]
    __members_by_value__: ta.ClassVar[ta.Mapping[V, str]]

    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], str):
            [name] = args
            return cls.__members_by_name__[name]
        raise TypeError((args, kwargs))
