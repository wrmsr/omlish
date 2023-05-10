import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .metaclass import Data
from .types import Conferrer
from .types import SUPER


ValueEnumT = ta.TypeVar('ValueEnumT', bound='ValueEnum')


class _MISSING(lang.Marker):
    pass


def _confer_enum_final(att, sub, sup, bases):
    return sub['abstract'] is dc.MISSING or not sub['abstract']


ENUM_SUPER_CONFERS = {a: SUPER for a in [
    'repr',
    'reorder',
    'eq',
    'allow_setattr',
    'kwonly',
    'slots',
    'aspects',
    'confer',
]}


class Enum(
    Data,
    abstract=True,
    eq=False,
    frozen=True,
    slots=True,
    no_weakref=True,
    confer={
        'abstract': True,
        'frozen': True,
        'confer': {
            'final': Conferrer(_confer_enum_final),
            'frozen': True,
            **ENUM_SUPER_CONFERS,
        },
    },
):
    pass


class ValueEnum(
    Data,
    abstract=True,
    eq=False,
    frozen=True,
    reorder=True,
    slots=True,
    no_weakref=True,
    confer={
        'final': True,
        'frozen': True,
        'reorder': True,
    },
):
    name: str = dc.field(_MISSING, check_type=(str, _MISSING), kwonly=True)

    Values: ta.ClassVar[ta.Type['_ValueEnums']]

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not lang.is_abstract_class(cls):
            cls.Values = lang.new_type(
                '_ValueEnums',
                (_ValueEnums[cls],),
                {'__dataclass_value_enum_types__': [cls]},
            )


class _ValueEnumsMeta(lang.enums._ValueEnumMeta):  # noqa

    class _Namespace(lang.SimpleMetaDict):

        def __init__(self, vtypes):
            super().__init__()
            self._vtypes = tuple(vtypes)

        def __setitem__(self, key, value):
            if isinstance(value, self._vtypes) and value.name is _MISSING:
                value = dc.replace(value, name=key)
            super().__setitem__(key, value)

    @classmethod
    def __prepare__(
            mcls,
            name: str,
            bases: ta.Tuple[type, ...],
            **kwargs: ta.Any,
    ) -> ta.MutableMapping[str, ta.Any]:
        s = set()
        for b in bases:
            for m in b.__mro__:
                al = m.__dict__.get('__dataclass_value_enum_types__')
                if al:
                    for a in al:
                        s.add(check.issubclass(a, ValueEnum))
        if s:
            return mcls._Namespace(s)  # noqa
        return {}


class _ValueEnums(lang.ValueEnum[ValueEnumT], metaclass=_ValueEnumsMeta):
    __dataclass_value_enum_types__: ta.Optional[ta.Collection[ta.Type[ValueEnum]]] = None

    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            [arg] = args
            if cls.__dataclass_value_enum_types__:  # noqa
                if isinstance(arg, tuple(cls.__dataclass_value_enum_types__)):  # noqa
                    return arg
            if isinstance(arg, str):
                return cls.__members_by_name__[arg]
        raise TypeError((args, kwargs))
