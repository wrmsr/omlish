import abc
import copy
import dataclasses as dc
import functools
import inspect
import itertools
import keyword
import re
import sys
import threading
import types
import typing as ta

from omlish import lang

from .fields import field_init
from .internals import FIELDS_ATTR
from .internals import FieldType
from .internals import HASH_ACTIONS
from .internals import HAS_DEFAULT_FACTORY
from .internals import PARAMS_ATTR
from .internals import POST_INIT_NAME
from .internals import recursive_repr
from .internals import tuple_str
from .params import ExField
from .params import ExParams
from .params import ex_fields
from .utils import Namespace
from .utils import create_fn


# init


def init_param(f: ExField) -> str:
    if not f.default.present and not f.default_factory.present:
        default = ''
    elif f.default.present:
        default = f'=__dataclass_dflt_{f.name}__'
    elif f.default_factory.present:
        default = '=__dataclass_HAS_DEFAULT_FACTORY__'
    return f'{f.name}:__dataclass_type_{f.name}__{default}'  # noqa


def init_fn(
        params: ExParams,
        fields: ta.Sequence[ExField],
        std_fields: ta.Sequence[ExField],
        kw_only_fields: ta.Sequence[ExField],
        has_post_init: bool,
        self_name: str,
        globals: Namespace,
) -> ta.Callable:
    seen_default = False
    for f in std_fields:
        if f.init:
            if not (f.default.present and f.default_factory.present):
                seen_default = True
            elif seen_default:
                raise TypeError(f'non-default argument {f.name!r} follows default argument')

    locals = {f'__dataclass_type_{f.name}__': f.type for f in fields}
    locals.update({
        '__dataclass_HAS_DEFAULT_FACTORY__': HAS_DEFAULT_FACTORY,
        '__dataclass_builtins_object__': object,
    })

    body_lines = []
    for f in fields:
        line = field_init(f, params.frozen, locals, self_name, params.slots)

        if line:
            body_lines.append(line)

    if has_post_init:
        params_str = ','.join(f.name for f in fields if f.field_type is FieldType.INIT)
        body_lines.append(f'{self_name}.{POST_INIT_NAME}({params_str})')

    if not body_lines:
        body_lines = ['pass']

    _init_params = [init_param(f) for f in std_fields]
    if kw_only_fields:
        _init_params += ['*']
        _init_params += [init_param(f) for f in kw_only_fields]

    return create_fn(
        '__init__',
        [self_name] + _init_params,
        body_lines,
        locals=locals,
        globals=globals,
        return_type=lang.empty(),
    )


# misc


def repr_fn(
        fields: ta.Sequence[ExField],
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
    return recursive_repr(fn)


def frozen_get_del_attr(
        cls: type,
        fields: ta.Sequence[ExField],
        globals: Namespace,
) -> ta.Tuple[ta.Callable, ta.Callable]:
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
    return [getattr(self, f.name) for f in ex_fields(self)]


def _dataclass_setstate(self, state):
    for field, value in zip(ex_fields(self), state):
        object.__setattr__(self, field.name, value)


def _get_slots(cls):
    sl = cls.__dict__.get('__slots__')
    if sl is None:
        return
    elif isinstance(sl, str):
        yield sl
    elif not hasattr(sl, '__next__'):
        yield from sl
    else:
        raise TypeError(f"Slots of '{cls.__name__}' cannot be determined")


def add_slots(
        cls: type,
        is_frozen: bool,
        weakref_slot: bool,
) -> type:
    if '__slots__' in cls.__dict__:
        raise TypeError(f'{cls.__name__} already specifies __slots__')

    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in ex_fields(cls))

    inherited_slots = set(
        itertools.chain.from_iterable(map(_get_slots, cls.__mro__[1:-1]))
    )

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
            cls.__getstate__ = _dataclass_getstate
        if '__setstate__' not in cls_dict:
            cls.__setstate__ = _dataclass_setstate

    return cls
