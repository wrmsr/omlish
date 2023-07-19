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
from .utils import create_fn


# init


def init_param(f: ExField) -> str:
    if not f.default.present and not f.default_factory.present:
        default = ''
    elif f.default.present:
        default = f'=__dataclass_dflt_{f.name}__'
    elif f.default_factory.present:
        default = '=__dataclass_HAS_DEFAULT_FACTORY__'
    return f'{f.name}:__dataclass_type_{f.name}__{default}'


def _init_fn(
        params: ExParams,
        fields: ta.Sequence[ExField],
        std_fields: ta.Sequence[ExField],
        kw_only_fields: ta.Sequence[ExField],
        has_post_init: bool,
        self_name: str,
        globals: ta.MutableMapping[str, ta.Any],
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


def repr_fn(fields: ta.Sequence[ExField], globals: ta.MutableMapping[str, ta.Any]):
    fn = _create_fn(
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


def frozen_get_del_attr(cls, fields, globals):
    locals = {
        'cls': cls,
        'FrozenInstanceError': FrozenInstanceError,
    }
    condition = 'type(self) is cls'
    if fields:
        condition += ' or name in {' + ', '.join(repr(f.name) for f in fields) + '}'
    return (
        _create_fn(
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
        _create_fn(
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


def cmp_fn(name, op, self_tuple, other_tuple, globals):
    return _create_fn(
        name,
        ('self', 'other'),
        [
            'if other.__class__ is self.__class__:',
            f' return {self_tuple}{op}{other_tuple}',
            'return NotImplemented',
        ],
        globals=globals,
    )
