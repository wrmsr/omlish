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


_MODULE_IDENTIFIER_RE = re.compile(r'^(?:\s*(\w+)\s*\.)?\s*(\w+)')


def _set_qualname(cls, value):
    if isinstance(value, types.FunctionType):
        value.__qualname__ = f"{cls.__qualname__}.{value.__name__}"
    return value


def _set_new_attribute(cls, name, value):
    if name in cls.__dict__:
        return True
    _set_qualname(cls, value)
    setattr(cls, name, value)
    return False


def _process_class(cls, params: dc._DataclassParams):
    fields = {}

    if cls.__module__ in sys.modules:
        globals = sys.modules[cls.__module__].__dict__
    else:
        globals = {}

    setattr(
        cls,
        PARAMS_ATTR,
        params,
    )

    any_frozen_base = False
    has_dataclass_bases = False
    for b in cls.__mro__[-1:0:-1]:
        base_fields = getattr(b, FIELDS_ATTR, None)
        if base_fields is not None:
            has_dataclass_bases = True
            for f in base_fields.values():
                fields[f.name] = f
            if getattr(b, PARAMS_ATTR).frozen:
                any_frozen_base = True

    cls_annotations = inspect.get_annotations(cls)

    cls_fields = []

    kw_only = params.kw_only
    kw_only_seen = False
    dataclasses = sys.modules[__name__]
    for name, type in cls_annotations.items():
        if (
                _is_kw_only(type, dataclasses)
                or (isinstance(type, str) and _is_type(type, cls, dataclasses, dataclasses.KW_ONLY, _is_kw_only))
        ):
            if kw_only_seen:
                raise TypeError(f'{name!r} is KW_ONLY, but KW_ONLY has already been specified')
            kw_only_seen = True
            kw_only = True
        else:
            cls_fields.append(_get_field(cls, name, type, kw_only))

    for f in cls_fields:
        fields[f.name] = f
        if isinstance(getattr(cls, f.name, None), dc.Field):
            if f.default is MISSING:
                delattr(cls, f.name)
            else:
                setattr(cls, f.name, f.default)

    for name, value in cls.__dict__.items():
        if isinstance(value, dc.Field) and not name in cls_annotations:
            raise TypeError(f'{name!r} is a field but has no type annotation')

    if has_dataclass_bases:
        if any_frozen_base and not params.frozen:
            raise TypeError('cannot inherit non-frozen dataclass from a frozen one')

        if not any_frozen_base and params.frozen:
            raise TypeError('cannot inherit frozen dataclass from a non-frozen one')

    setattr(cls, FIELDS_ATTR, fields)

    class_hash = cls.__dict__.get('__hash__', MISSING)
    has_explicit_hash = not (class_hash is MISSING or (class_hash is None and '__eq__' in cls.__dict__))

    if params.order and not params.eq:
        raise ValueError('eq must be true if order is true')

    all_init_fields = [f for f in fields.values() if f._field_type in (_FIELD, _FIELD_INITVAR)]
    std_init_fields, kw_only_init_fields = _fields_in_init_order(all_init_fields)

    if params.init:
        has_post_init = hasattr(cls, POST_INIT_NAME)

        _set_new_attribute(
            cls,
            '__init__',
            _init_fn(
                all_init_fields,
                std_init_fields,
                kw_only_init_fields,
                params.frozen,
                has_post_init,
                '__dataclass_self__' if 'self' in fields else 'self',
                globals,
                params.slots,
            ),
        )

    field_list = [f for f in fields.values() if f._field_type is _FIELD]

    if params.repr:
        flds = [f for f in field_list if f.repr]
        _set_new_attribute(cls, '__repr__', _repr_fn(flds, globals))

    if params.eq:
        # flds = [f for f in field_list if f.compare]
        # self_tuple = tuple_str('self', flds)
        # other_tuple = tuple_str('other', flds)
        # _set_new_attribute(cls, '__eq__', _cmp_fn('__eq__', '==', self_tuple, other_tuple, globals=globals))
        cmp_fields = (field for field in field_list if field.compare)
        terms = [f'self.{field.name}==other.{field.name}' for field in cmp_fields]
        field_comparisons = ' and '.join(terms) or 'True'
        body = [f'if other.__class__ is self.__class__:',
                f' return {field_comparisons}',
                f'return NotImplemented']
        func = _create_fn('__eq__', ('self', 'other'), body, globals=globals)
        _set_new_attribute(cls, '__eq__', func)

    if params.order:
        flds = [f for f in field_list if f.compare]
        self_tuple = tuple_str('self', flds)
        other_tuple = tuple_str('other', flds)
        for name, op in [
            ('__lt__', '<'),
            ('__le__', '<='),
            ('__gt__', '>'),
            ('__ge__', '>='),
        ]:
            if _set_new_attribute(cls, name, _cmp_fn(name, op, self_tuple, other_tuple, globals=globals)):
                raise TypeError(f'Cannot overwrite attribute {name} in class {cls.__name__}. Consider using functools.total_ordering')  # noqa

    if params.frozen:
        for fn in _frozen_get_del_attr(cls, field_list, globals):
            if _set_new_attribute(cls, fn.__name__, fn):
                raise TypeError(f'Cannot overwrite attribute {fn.__name__} in class {cls.__name__}')

    hash_action = HASH_ACTIONS[(
        bool(params.unsafe_hash),
        bool(params.eq),
        bool(params.frozen),
        has_explicit_hash,
    )]
    if hash_action:
        cls.__hash__ = hash_action(cls, field_list, globals)

    if not getattr(cls, '__doc__'):
        try:
            text_sig = str(inspect.signature(cls)).replace(' -> None', '')
        except (TypeError, ValueError):
            text_sig = ''
        cls.__doc__ = (cls.__name__ + text_sig)

    if params.match_args:
        _set_new_attribute(cls, '__match_args__', tuple(f.name for f in std_init_fields))

    if params.weakref_slot and not params.slots:
        raise TypeError('weakref_slot is True but slots is False')
    if params.slots:
        cls = _add_slots(cls, params.frozen, params.weakref_slot)

    abc.update_abstractmethods(cls)

    return cls




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
