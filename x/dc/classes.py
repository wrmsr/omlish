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

from .internals import FIELDS_ATTR
from .internals import PARAMS_ATTR
from .internals import POST_INIT_NAME
from .internals import HASH_ACTIONS
from .internals import recursive_repr
from .internals import tuple_str

from .params import ExField
from .params import ExParams


# init


def init_param(f):
    if f.default is MISSING and f.default_factory is MISSING:
        default = ''
    elif f.default is not MISSING:
        default = f'=__dataclass_dflt_{f.name}__'
    elif f.default_factory is not MISSING:
        default = '=__dataclass_HAS_DEFAULT_FACTORY__'
    return f'{f.name}:__dataclass_type_{f.name}__{default}'


def _init_fn(
        fields,
        std_fields,
        kw_only_fields,
        frozen,
        has_post_init,
        self_name,
        globals,
        slots,
):
    seen_default = False
    for f in std_fields:
        if f.init:
            if not (f.default is MISSING and f.default_factory is MISSING):
                seen_default = True
            elif seen_default:
                raise TypeError(f'non-default argument {f.name!r} follows default argument')

    locals = {f'__dataclass_type_{f.name}__': f.type for f in fields}
    locals.update({
        '__dataclass_HAS_DEFAULT_FACTORY__': _HAS_DEFAULT_FACTORY,
        '__dataclass_builtins_object__': object,
    })

    body_lines = []
    for f in fields:
        line = _field_init(f, frozen, locals, self_name, slots)

        if line:
            body_lines.append(line)

    if has_post_init:
        params_str = ','.join(f.name for f in fields if f._field_type is _FIELD_INITVAR)
        body_lines.append(f'{self_name}.{POST_INIT_NAME}({params_str})')

    if not body_lines:
        body_lines = ['pass']

    _init_params = [_init_param(f) for f in std_fields]
    if kw_only_fields:
        _init_params += ['*']
        _init_params += [_init_param(f) for f in kw_only_fields]

    return _create_fn(
        '__init__',
        [self_name] + _init_params,
        body_lines,
        locals=locals,
        globals=globals,
        return_type=None,
        )
