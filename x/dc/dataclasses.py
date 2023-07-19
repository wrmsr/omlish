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


##


FrozenInstanceError = dc.FrozenInstanceError

MISSING = dc.MISSING
KW_ONLY = dc.KW_ONLY

InitVar = dc.InitVar
Field = dc.Field

# field = dc.field

# dataclass = dc.dataclass
# make_dataclass = dc.make_dataclass

fields = dc.fields

is_dataclass = dc.is_dataclass

asdict = dc.asdict
astuple = dc.astuple

replace = dc.replace


##


_HAS_DEFAULT_FACTORY = dc._HAS_DEFAULT_FACTORY
_FIELD = dc._FIELD
_FIELD_CLASSVAR = dc._FIELD_CLASSVAR
_FIELD_INITVAR = dc._FIELD_INITVAR





def dataclass(
        cls=None,
        /,
        *,
        init=True,
        repr=True,
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,
        match_args=True,
        kw_only=False,
        slots=False,
        weakref_slot=False,
):
    def wrap(cls):
        return _process_class(cls, dc._DataclassParams(
            init,
            repr,
            eq,
            order,
            unsafe_hash,
            frozen,
            match_args,
            kw_only,
            slots,
            weakref_slot,
        ))

    if cls is None:
        return wrap

    return wrap(cls)


def make_dataclass(
        cls_name,
        fields,
        *,
        bases=(),
        namespace=None,
        init=True,
        repr=True,
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,
        match_args=True,
        kw_only=False,
        slots=False,
        weakref_slot=False,
        module=None,
):
    if namespace is None:
        namespace = {}

    seen = set()
    annotations = {}
    defaults = {}
    for item in fields:
        if isinstance(item, str):
            name = item
            tp = 'typing.Any'
        elif len(item) == 2:
            name, tp, = item
        elif len(item) == 3:
            name, tp, spec = item
            defaults[name] = spec
        else:
            raise TypeError(f'Invalid field: {item!r}')
        if not isinstance(name, str) or not name.isidentifier():
            raise TypeError(f'Field names must be valid identifiers: {name!r}')
        if keyword.iskeyword(name):
            raise TypeError(f'Field names must not be keywords: {name!r}')
        if name in seen:
            raise TypeError(f'Field name duplicated: {name!r}')

        seen.add(name)
        annotations[name] = tp

    def exec_body_callback(ns):
        ns.update(namespace)
        ns.update(defaults)
        ns['__annotations__'] = annotations

    cls = types.new_class(cls_name, bases, {}, exec_body_callback)

    if module is None:
        try:
            module = sys._getframemodulename(1) or '__main__'
        except AttributeError:
            try:
                module = sys._getframe(1).f_globals.get('__name__', '__main__')
            except (AttributeError, ValueError):
                pass
    if module is not None:
        cls.__module__ = module

    return dataclass(
        cls,
        init=init,
        repr=repr,
        eq=eq,
        order=order,
        unsafe_hash=unsafe_hash,
        frozen=frozen,
        match_args=match_args,
        kw_only=kw_only,
        slots=slots,
        weakref_slot=weakref_slot,
    )
