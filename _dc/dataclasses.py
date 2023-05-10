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

from . import polyfill as pf


__all__ = [
    'dataclass',
    'field',
    'Field',
    'FrozenInstanceError',
    'InitVar',
    'KW_ONLY',
    'MISSING',

    'fields',
    'asdict',
    'astuple',
    'make_dataclass',
    'replace',
    'is_dataclass',
]


class FrozenInstanceError(AttributeError):
    pass


_HAS_DEFAULT_FACTORY = getattr(dc, '_HAS_DEFAULT_FACTORY')


MISSING = dc.MISSING


if hasattr(dc, 'KW_ONLY'):
    KW_ONLY = dc.KW_ONLY
else:
    class _KW_ONLY_TYPE:
        pass

    KW_ONLY = _KW_ONLY_TYPE()

_EMPTY_METADATA = types.MappingProxyType({})


class _FIELD_BASE:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


_FIELD = _FIELD_BASE('_FIELD')
_FIELD_CLASSVAR = _FIELD_BASE('_FIELD_CLASSVAR')
_FIELD_INITVAR = _FIELD_BASE('_FIELD_INITVAR')

_FIELDS = '__dataclass_fields__'

_PARAMS = '__dataclass_params__'

_POST_INIT_NAME = '__post_init__'

_MODULE_IDENTIFIER_RE = re.compile(r'^(?:\s*(\w+)\s*\.)?\s*(\w+)')

_ATOMIC_TYPES = frozenset({
    pf.NoneType,
    bool,
    int,
    float,
    str,

    complex,
    bytes,

    pf.EllipsisType,
    pf.NotImplementedType,
    types.CodeType,
    types.BuiltinFunctionType,
    types.FunctionType,
    type,
    range,
    property,
})


def _recursive_repr(user_function):
    repr_running = set()

    @functools.wraps(user_function)
    def wrapper(self):
        key = id(self), threading.get_ident()
        if key in repr_running:
            return '...'
        repr_running.add(key)
        try:
            result = user_function(self)
        finally:
            repr_running.discard(key)
        return result

    return wrapper


class InitVar:
    __slots__ = ('type',)

    def __init__(self, type):
        self.type = type

    def __repr__(self):
        if isinstance(self.type, type):
            type_name = self.type.__name__
        else:

            type_name = repr(self.type)
        return f'dataclasses.InitVar[{type_name}]'

    def __class_getitem__(cls, type):
        return InitVar(type)


class Field:
    __slots__ = (
        'name',
        'type',
        'default',
        'default_factory',
        'repr',
        'hash',
        'init',
        'compare',
        'metadata',
        'kw_only',
        '_field_type',
    )

    def __init__(
            self,
            default,
            default_factory,
            init,
            repr,
            hash,
            compare,
            metadata,
            kw_only,
    ):
        self.name = None
        self.type = None
        self.default = default
        self.default_factory = default_factory
        self.init = init
        self.repr = repr
        self.hash = hash
        self.compare = compare
        self.metadata = (_EMPTY_METADATA if metadata is None else types.MappingProxyType(metadata))
        self.kw_only = kw_only
        self._field_type = None

    @_recursive_repr
    def __repr__(self):
        return (
            'Field('
            f'name={self.name!r},'
            f'type={self.type!r},'
            f'default={self.default!r},'
            f'default_factory={self.default_factory!r},'
            f'init={self.init!r},'
            f'repr={self.repr!r},'
            f'hash={self.hash!r},'
            f'compare={self.compare!r},'
            f'metadata={self.metadata!r},'
            f'kw_only={self.kw_only!r},'
            f'_field_type={self._field_type}'
            ')'
        )

    def __set_name__(self, owner, name):
        func = getattr(type(self.default), '__set_name__', None)
        if func:
            func(self.default, owner, name)

    __class_getitem__ = classmethod(types.GenericAlias)


class _DataclassParams:
    __slots__ = (
        'init',
        'repr',
        'eq',
        'order',
        'unsafe_hash',
        'frozen',
        'match_args',
        'kw_only',
        'slots',
        'weakref_slot',
    )

    def __init__(
            self,
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
    ):
        self.init = init
        self.repr = repr
        self.eq = eq
        self.order = order
        self.unsafe_hash = unsafe_hash
        self.frozen = frozen
        self.match_args = match_args
        self.kw_only = kw_only
        self.slots = slots
        self.weakref_slot = weakref_slot

    def __repr__(self):
        return (
            '_DataclassParams('
            f'init={self.init!r},'
            f'repr={self.repr!r},'
            f'eq={self.eq!r},'
            f'order={self.order!r},'
            f'unsafe_hash={self.unsafe_hash!r},'
            f'frozen={self.frozen!r},'
            f'match_args={self.match_args!r},'
            f'kw_only={self.kw_only!r},'
            f'slots={self.slots!r},'
            f'weakref_slot={self.weakref_slot!r}'
            ')'
        )


def field(
        *,
        default=MISSING,
        default_factory=MISSING,
        init=True,
        repr=True,
        hash=None,
        compare=True,
        metadata=None,
        kw_only=MISSING,
):
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')
    return Field(
        default,
        default_factory,
        init,
        repr,
        hash,
        compare,
        metadata,
        kw_only,
    )


def _fields_in_init_order(fields):
    return (
        tuple(f for f in fields if f.init and not f.kw_only),
        tuple(f for f in fields if f.init and f.kw_only),
    )


def _tuple_str(obj_name, fields):
    if not fields:
        return '()'
    return f'({",".join([f"{obj_name}.{f.name}" for f in fields])},)'


def _create_fn(
        name,
        args,
        body,
        *,
        globals=None,
        locals=None,
        return_type=MISSING,
):
    if locals is None:
        locals = {}
    return_annotation = ''
    if return_type is not MISSING:
        locals['__dataclass_return_type__'] = return_type
        return_annotation = '->__dataclass_return_type__'
    args = ','.join(args)
    body = '\n'.join(f'  {b}' for b in body)

    txt = f' def {name}({args}){return_annotation}:\n{body}'

    local_vars = ', '.join(locals.keys())
    txt = f"def __create_fn__({local_vars}):\n{txt}\n return {name}"
    ns = {}
    exec(txt, globals, ns)
    return ns['__create_fn__'](**locals)


def _field_assign(frozen, name, value, self_name):
    if frozen:
        return f'__dataclass_builtins_object__.__setattr__({self_name},{name!r},{value})'
    return f'{self_name}.{name}={value}'


def _field_init(f, frozen, globals, self_name, slots):
    default_name = f'__dataclass_dflt_{f.name}__'
    if f.default_factory is not MISSING:
        if f.init:
            globals[default_name] = f.default_factory
            value = (f'{default_name}() '
                     f'if {f.name} is __dataclass_HAS_DEFAULT_FACTORY__ '
                     f'else {f.name}')
        else:
            globals[default_name] = f.default_factory
            value = f'{default_name}()'
    else:
        if f.init:
            if f.default is MISSING:
                value = f.name
            elif f.default is not MISSING:
                globals[default_name] = f.default
                value = f.name
        else:
            if slots and f.default is not MISSING:
                globals[default_name] = f.default
                value = default_name
            else:
                return None

    if f._field_type is _FIELD_INITVAR:
        return None

    return _field_assign(frozen, f.name, value, self_name)


def _init_param(f):
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
                raise TypeError(f'non-default argument {f.name!r} '
                                'follows default argument')

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
        body_lines.append(f'{self_name}.{_POST_INIT_NAME}({params_str})')

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


def _repr_fn(fields, globals):
    fn = _create_fn(
        '__repr__',
        ('self',),
        [('return self.__class__.__qualname__ + f"(' +
          ', '.join([f"{f.name}={{self.{f.name}!r}}" for f in fields]) +
          ')"')],
        globals=globals,
    )
    return _recursive_repr(fn)


def _frozen_get_del_attr(cls, fields, globals):
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
            (f'if {condition}:',
             ' raise FrozenInstanceError(f"cannot assign to field {name!r}")',
             f'super(cls, self).__setattr__(name, value)'),
            locals=locals,
            globals=globals,
        ),
        _create_fn(
            '__delattr__',
            ('self', 'name'),
            (f'if {condition}:',
             ' raise FrozenInstanceError(f"cannot delete field {name!r}")',
             f'super(cls, self).__delattr__(name)'),
            locals=locals,
            globals=globals,
        ),
    )


def _cmp_fn(name, op, self_tuple, other_tuple, globals):
    return _create_fn(
        name,
        ('self', 'other'),
        ['if other.__class__ is self.__class__:',
         f' return {self_tuple}{op}{other_tuple}',
         'return NotImplemented'],
        globals=globals,
    )


def _hash_fn(fields, globals):
    self_tuple = _tuple_str('self', fields)
    return _create_fn(
        '__hash__',
        ('self',),
        [f'return hash({self_tuple})'],
        globals=globals,
    )


def _is_classvar(a_type, typing):
    return (
            a_type is typing.ClassVar
            or (type(a_type) is typing._GenericAlias and a_type.__origin__ is typing.ClassVar)
    )


def _is_initvar(a_type, dataclasses):
    return (
            a_type is dataclasses.InitVar
            or type(a_type) is dataclasses.InitVar
    )


def _is_kw_only(a_type, dataclasses):
    return a_type is dataclasses.KW_ONLY


def _is_type(annotation, cls, a_module, a_type, is_type_predicate):
    match = _MODULE_IDENTIFIER_RE.match(annotation)
    if match:
        ns = None
        module_name = match.group(1)
        if not module_name:
            ns = sys.modules.get(cls.__module__).__dict__
        else:
            module = sys.modules.get(cls.__module__)
            if module and module.__dict__.get(module_name) is a_module:
                ns = sys.modules.get(a_type.__module__).__dict__
        if ns and is_type_predicate(ns.get(match.group(2)), a_module):
            return True
    return False


def _get_field(cls, a_name, a_type, default_kw_only):
    default = getattr(cls, a_name, MISSING)
    if isinstance(default, Field):
        f = default
    else:
        if isinstance(default, types.MemberDescriptorType):

            default = MISSING
        f = field(default=default)

    f.name = a_name
    f.type = a_type

    f._field_type = _FIELD

    typing = sys.modules.get('typing')
    if typing:
        if (
                _is_classvar(a_type, typing)
                or (isinstance(f.type, str) and _is_type(f.type, cls, typing, typing.ClassVar, _is_classvar))
        ):
            f._field_type = _FIELD_CLASSVAR

    if f._field_type is _FIELD:
        dataclasses = sys.modules[__name__]
        if (
                _is_initvar(a_type, dataclasses)
                or (isinstance(f.type, str) and _is_type(f.type, cls, dataclasses, dataclasses.InitVar, _is_initvar))
        ):
            f._field_type = _FIELD_INITVAR

    if f._field_type in (_FIELD_CLASSVAR, _FIELD_INITVAR):
        if f.default_factory is not MISSING:
            raise TypeError(f'field {f.name} cannot have a default factory')

    if f._field_type in (_FIELD, _FIELD_INITVAR):
        if f.kw_only is MISSING:
            f.kw_only = default_kw_only
    else:
        assert f._field_type is _FIELD_CLASSVAR
        if f.kw_only is not MISSING:
            raise TypeError(f'field {f.name} is a ClassVar but specifies kw_only')

    if f._field_type is _FIELD and f.default.__class__.__hash__ is None:
        raise ValueError(f'mutable default {type(f.default)} for field {f.name} is not allowed: use default_factory')

    return f


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


def _hash_set_none(cls, fields, globals):
    return None


def _hash_add(cls, fields, globals):
    flds = [f for f in fields if (f.compare if f.hash is None else f.hash)]
    return _set_qualname(cls, _hash_fn(flds, globals))


def _hash_exception(cls, fields, globals):
    raise TypeError(f'Cannot overwrite attribute __hash__  in class {cls.__name__}')


_hash_action = {
    (False, False, False, False): None,
    (False, False, False, True): None,
    (False, False, True, False): None,
    (False, False, True, True): None,
    (False, True, False, False): _hash_set_none,
    (False, True, False, True): None,
    (False, True, True, False): _hash_add,
    (False, True, True, True): None,
    (True, False, False, False): _hash_add,
    (True, False, False, True): _hash_exception,
    (True, False, True, False): _hash_add,
    (True, False, True, True): _hash_exception,
    (True, True, False, False): _hash_add,
    (True, True, False, True): _hash_exception,
    (True, True, True, False): _hash_add,
    (True, True, True, True): _hash_exception,
}


def _process_class(cls, params: _DataclassParams):
    fields = {}

    if cls.__module__ in sys.modules:
        globals = sys.modules[cls.__module__].__dict__
    else:
        globals = {}

    setattr(
        cls,
        _PARAMS,
        params,
    )

    any_frozen_base = False
    has_dataclass_bases = False
    for b in cls.__mro__[-1:0:-1]:
        base_fields = getattr(b, _FIELDS, None)
        if base_fields is not None:
            has_dataclass_bases = True
            for f in base_fields.values():
                fields[f.name] = f
            if getattr(b, _PARAMS).frozen:
                any_frozen_base = True

    cls_annotations = pf.get_annotations(cls)

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
        if isinstance(getattr(cls, f.name, None), Field):
            if f.default is MISSING:
                delattr(cls, f.name)
            else:
                setattr(cls, f.name, f.default)

    for name, value in cls.__dict__.items():
        if isinstance(value, Field) and not name in cls_annotations:
            raise TypeError(f'{name!r} is a field but has no type annotation')

    if has_dataclass_bases:
        if any_frozen_base and not params.frozen:
            raise TypeError('cannot inherit non-frozen dataclass from a frozen one')

        if not any_frozen_base and params.frozen:
            raise TypeError('cannot inherit frozen dataclass from a non-frozen one')

    setattr(cls, _FIELDS, fields)

    class_hash = cls.__dict__.get('__hash__', MISSING)
    has_explicit_hash = not (class_hash is MISSING or (class_hash is None and '__eq__' in cls.__dict__))

    if params.order and not params.eq:
        raise ValueError('eq must be true if order is true')

    all_init_fields = [f for f in fields.values() if f._field_type in (_FIELD, _FIELD_INITVAR)]
    std_init_fields, kw_only_init_fields = _fields_in_init_order(all_init_fields)

    if params.init:
        has_post_init = hasattr(cls, _POST_INIT_NAME)

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
        flds = [f for f in field_list if f.compare]
        self_tuple = _tuple_str('self', flds)
        other_tuple = _tuple_str('other', flds)
        _set_new_attribute(cls, '__eq__', _cmp_fn('__eq__', '==', self_tuple, other_tuple, globals=globals))

    if params.order:
        flds = [f for f in field_list if f.compare]
        self_tuple = _tuple_str('self', flds)
        other_tuple = _tuple_str('other', flds)
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

    hash_action = _hash_action[(
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

    pf.update_abstractmethods(cls)

    return cls


def _dataclass_getstate(self):
    return [getattr(self, f.name) for f in fields(self)]


def _dataclass_setstate(self, state):
    for field, value in zip(fields(self), state):
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


def _add_slots(cls, is_frozen, weakref_slot):
    if '__slots__' in cls.__dict__:
        raise TypeError(f'{cls.__name__} already specifies __slots__')

    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in fields(cls))

    inherited_slots = set(
        itertools.chain.from_iterable(map(_get_slots, cls.__mro__[1:-1]))
    )

    cls_dict["__slots__"] = tuple(
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
        return _process_class(cls, _DataclassParams(
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


def fields(class_or_instance):
    try:
        fields = getattr(class_or_instance, _FIELDS)
    except AttributeError:
        raise TypeError('must be called with a dataclass type or instance') from None
    return tuple(f for f in fields.values() if f._field_type is _FIELD)


def _is_dataclass_instance(obj):
    return hasattr(type(obj), _FIELDS)


def is_dataclass(obj):
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, _FIELDS)


def asdict(obj, *, dict_factory=dict):
    if not _is_dataclass_instance(obj):
        raise TypeError("asdict() should be called on dataclass instances")
    return _asdict_inner(obj, dict_factory)


def _asdict_inner(obj, dict_factory):
    if type(obj) in _ATOMIC_TYPES:
        return obj
    elif _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _asdict_inner(getattr(obj, f.name), dict_factory)
            result.append((f.name, value))
        return dict_factory(result)
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[_asdict_inner(v, dict_factory) for v in obj])
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_asdict_inner(v, dict_factory) for v in obj)
    elif isinstance(obj, dict):
        if hasattr(type(obj), 'default_factory'):
            result = type(obj)(getattr(obj, 'default_factory'))
            for k, v in obj.items():
                result[_asdict_inner(k, dict_factory)] = _asdict_inner(v, dict_factory)
            return result
        return type(obj)((_asdict_inner(k, dict_factory), _asdict_inner(v, dict_factory)) for k, v in obj.items())
    else:
        return copy.deepcopy(obj)


def astuple(obj, *, tuple_factory=tuple):
    if not _is_dataclass_instance(obj):
        raise TypeError("astuple() should be called on dataclass instances")
    return _astuple_inner(obj, tuple_factory)


def _astuple_inner(obj, tuple_factory):
    if type(obj) in _ATOMIC_TYPES:
        return obj
    elif _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _astuple_inner(getattr(obj, f.name), tuple_factory)
            result.append(value)
        return tuple_factory(result)
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[_astuple_inner(v, tuple_factory) for v in obj])
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_astuple_inner(v, tuple_factory) for v in obj)
    elif isinstance(obj, dict):
        obj_type = type(obj)
        if hasattr(obj_type, 'default_factory'):
            result = obj_type(getattr(obj, 'default_factory'))
            for k, v in obj.items():
                result[_astuple_inner(k, tuple_factory)] = _astuple_inner(v, tuple_factory)
            return result
        return obj_type((_astuple_inner(k, tuple_factory), _astuple_inner(v, tuple_factory)) for k, v in obj.items())
    else:
        return copy.deepcopy(obj)


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


def replace(obj, /, **changes):
    if not _is_dataclass_instance(obj):
        raise TypeError("replace() should be called on dataclass instances")

    for f in getattr(obj, _FIELDS).values():
        if f._field_type is _FIELD_CLASSVAR:
            continue

        if not f.init:
            if f.name in changes:
                raise ValueError(f'field {f.name} is declared with init=False, it cannot be specified with replace()')
            continue

        if f.name not in changes:
            if f._field_type is _FIELD_INITVAR and f.default is MISSING:
                raise ValueError(f"InitVar {f.name!r} " 'must be specified with replace()')
            changes[f.name] = getattr(obj, f.name)

    return obj.__class__(**changes)
