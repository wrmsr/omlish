import dataclasses as dc
import itertools
import reprlib
import typing as ta

from .utils import Namespace
from .utils import create_fn


MISSING = dc.MISSING


# misc


def repr_fn(
        fields: ta.Sequence[dc.Field],
        globals: Namespace,
) -> ta.Callable:
    fn = create_fn(
        '__repr__',
        ('self',),
        [
            'return f"{self.__class__.__qualname__}(' +
            ', '.join([f"{f.name}={{self.{f.name}!r}}" for f in fields]) +
            ')"'
        ],
        globals=globals,
    )
    return reprlib.recursive_repr()(fn)


def frozen_get_del_attr(
        cls: type,
        fields: ta.Sequence[dc.Field],
        globals: Namespace,
) -> tuple[ta.Callable, ta.Callable]:
    locals = {
        'cls': cls,
        'FrozenInstanceError': dc.FrozenInstanceError,
    }
    condition = 'type(self) is cls'
    if fields:
        condition += ' or name in {' + ', '.join(repr(f.name) for f in fields) + '}'
    return (
        create_fn(
            '__setattr__',
            ('self', 'name', 'value'),
            [
                f'if {condition}:',
                ' raise FrozenInstanceError(f"cannot assign to field {name!r}")',
                f'super(cls, self).__setattr__(name, value)',
            ],
            locals=locals,
            globals=globals,
        ),
        create_fn(
            '__delattr__',
            ('self', 'name'),
            [
                f'if {condition}:',
                ' raise FrozenInstanceError(f"cannot delete field {name!r}")',
                f'super(cls, self).__delattr__(name)',
            ],
            locals=locals,
            globals=globals,
        ),
    )


def cmp_fn(
        name: str,
        op: str,
        self_tuple: str,
        other_tuple: str,
        globals: Namespace,
) -> ta.Callable:
    return create_fn(
        name,
        ('self', 'other'),
        [
            'if other.__class__ is self.__class__:',
            f' return {self_tuple}{op}{other_tuple}',
            'return NotImplemented',
        ],
        globals=globals,
    )


# slots


def _dataclass_getstate(self):
    return [getattr(self, f.name) for f in dc.fields(self)]


def _dataclass_setstate(self, state):
    for field, value in zip(dc.fields(self), state):
        object.__setattr__(self, field.name, value)


def _get_slots(cls):
    match cls.__dict__.get('__slots__'):
        # A class which does not define __slots__ at all is equivalent to a class defining
        #   __slots__ = ('__dict__', '__weakref__')
        # `__dictoffset__` and `__weakrefoffset__` can tell us whether the base type has dict/weakref slots, in a way
        # that works correctly for both Python classes and C extension types. Extension types don't use `__slots__` for
        # slot creation
        case None:
            slots = []
            if getattr(cls, '__weakrefoffset__', -1) != 0:
                slots.append('__weakref__')
            if getattr(cls, '__dictrefoffset__', -1) != 0:
                slots.append('__dict__')
            yield from slots
        case str(slot):
            yield slot
        # Slots may be any iterable, but we cannot handle an iterator because it will already be (partially) consumed.
        case iterable if not hasattr(iterable, '__next__'):
            yield from iterable
        case _:
            raise TypeError(f"Slots of '{cls.__name__}' cannot be determined")


def add_slots(
        cls: type,
        is_frozen: bool,
        weakref_slot: bool,
) -> type:
    if '__slots__' in cls.__dict__:
        raise TypeError(f'{cls.__name__} already specifies __slots__')

    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in dc.fields(cls))  # noqa

    inherited_slots = set(itertools.chain.from_iterable(map(_get_slots, cls.__mro__[1:-1])))

    cls_dict['__slots__'] = tuple(
        itertools.filterfalse(
            inherited_slots.__contains__,
            itertools.chain(
                field_names,
                ('__weakref__',) if weakref_slot else ()
            )
        ),
    )

    for field_name in field_names:
        cls_dict.pop(field_name, None)

    cls_dict.pop('__dict__', None)
    cls_dict.pop('__weakref__', None)

    qualname = getattr(cls, '__qualname__', None)
    cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    if qualname is not None:
        cls.__qualname__ = qualname

    if is_frozen:
        if '__getstate__' not in cls_dict:
            cls.__getstate__ = _dataclass_getstate  # type: ignore
        if '__setstate__' not in cls_dict:
            cls.__setstate__ = _dataclass_setstate  # type: ignore

    return cls
