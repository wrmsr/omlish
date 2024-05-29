import abc
import collections.abc
import dataclasses as dc
import inspect
import itertools
import reprlib
import sys
import typing as ta

from ... import cached
from ... import check
from ... import lang
from .fields import field_assign
from .fields import field_type
from .fields import preprocess_field
from .init import InitBuilder
from .init import get_init_fields
from .internals import FIELDS_ATTR
from .internals import FieldType
from .internals import HASH_ACTIONS
from .internals import PARAMS_ATTR
from .internals import POST_INIT_NAME
from .internals import Params
from .internals import is_kw_only
from .internals import tuple_str
from .metadata import METADATA_ATTR
from .metadata import get_merged_metadata
from .params import ParamsExtras
from .params import get_field_extras
from .params import get_params12
from .replace import _replace
from .utils import Namespace
from .utils import create_fn
from .utils import set_new_attribute


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


# process


class ClassProcessor:
    def __init__(self, cls: type) -> None:
        super().__init__()

        self._cls = check.isinstance(cls, type)

        self._params = check.isinstance(self._cls.__dict__[PARAMS_ATTR], Params)  # type: ignore
        self._cls_metadata = check.isinstance(self._cls.__dict__[METADATA_ATTR], collections.abc.Mapping)
        self._params12 = get_params12(self._cls)
        self._params_extras = check.isinstance(self._cls_metadata[ParamsExtras], ParamsExtras)  # type: ignore  # noqa
        self._merged_metadata = get_merged_metadata(self._cls)

    @cached.property
    def _globals(self) -> Namespace:
        if self._cls.__module__ in sys.modules:
            return sys.modules[self._cls.__module__].__dict__
        else:
            return {}

    def _check_params(self) -> None:
        if self._params.order and not self._params.eq:
            raise ValueError('eq must be true if order is true')

    def _check_frozen_bases(self) -> None:
        all_frozen_bases = None
        any_frozen_base = False
        has_dataclass_bases = False
        for b in self._cls.__mro__[-1:0:-1]:
            base_fields = getattr(b, FIELDS_ATTR, None)
            if base_fields is not None:
                has_dataclass_bases = True
                if all_frozen_bases is None:
                    all_frozen_bases = True
                current_frozen = getattr(b, PARAMS_ATTR).frozen
                all_frozen_bases = all_frozen_bases and current_frozen
                any_frozen_base = any_frozen_base or current_frozen

        if has_dataclass_bases:
            if any_frozen_base and not self._params.frozen:
                raise TypeError('cannot inherit non-frozen dataclass from a frozen one')

            if all_frozen_bases is False and self._params.frozen:
                raise TypeError('cannot inherit frozen dataclass from a non-frozen one')

    @cached.property
    def _cls_annotations(self) -> dict[str, ta.Any]:
        return inspect.get_annotations(self._cls)

    @lang.cached_nullary
    def _process_fields(self) -> dict[str, dc.Field]:
        fields: dict[str, dc.Field] = {}

        for b in self._cls.__mro__[-1:0:-1]:
            base_fields = getattr(b, FIELDS_ATTR, None)
            if base_fields is not None:
                for f in base_fields.values():
                    fields[f.name] = f

        cls_fields: list[dc.Field] = []

        kw_only = self._params12.kw_only
        kw_only_seen = False
        for name, type in self._cls_annotations.items():
            if is_kw_only(self._cls, type):
                if kw_only_seen:
                    raise TypeError(f'{name!r} is KW_ONLY, but KW_ONLY has already been specified')
                kw_only_seen = True
                kw_only = True
            else:
                cls_fields.append(preprocess_field(self._cls, name, type, kw_only))

        for f in cls_fields:
            fields[f.name] = f
            if isinstance(getattr(self._cls, f.name, None), dc.Field):
                if f.default is MISSING:
                    delattr(self._cls, f.name)
                else:
                    setattr(self._cls, f.name, f.default)

        for name, value in self._cls.__dict__.items():
            if isinstance(value, dc.Field) and name not in self._cls_annotations:
                raise TypeError(f'{name!r} is a field but has no type annotation')

        return fields

    @lang.cached_nullary
    def _fields(self) -> dict[str, dc.Field]:
        return self._process_fields()

    @lang.cached_nullary
    def _field_list(self) -> ta.Sequence[dc.Field]:
        return [f for f in self._process_fields().values() if field_type(f) is FieldType.INSTANCE]

    def _process_init(self) -> None:
        if not self._params.init:
            return

        has_post_init = hasattr(self._cls, POST_INIT_NAME)
        self_name = '__dataclass_self__' if 'self' in self._fields() else 'self'

        init = InitBuilder(
            self._params,
            self._params12,
            self._params_extras,
            self._merged_metadata,
            self._fields(),
            has_post_init,
            self_name,
            self._globals,
        ).build()
        set_new_attribute(
            self._cls,
            '__init__',
            init,
        )

    def _process_overrides(self) -> None:
        for f in self._field_list():
            fx = get_field_extras(f)
            if not fx.override:
                continue

            if self._params12.slots:
                raise TypeError

            self_name = '__dataclass_self__' if 'self' in self._fields() else 'self'

            getter = create_fn(
                f.name,
                (self_name,),
                [f'return {self_name}.__dict__[{f.name!r}]'],
                globals=self._globals,
                return_type=lang.just(f.type),
            )
            prop = property(getter)

            if not self._params.frozen:
                setter = create_fn(
                    f.name,
                    (self_name, f'{f.name}: __dataclass_type_{f.name}__'),
                    [field_assign(self._params.frozen, f.name, f.name, self_name, fx.override)],
                    globals=self._globals,
                    locals={f'__dataclass_type_{f.name}__': f.type},
                    return_type=lang.just(None),
                )
                prop = prop.setter(setter)

            set_new_attribute(
                self._cls,
                f.name,
                prop,
            )

    def _process_repr(self) -> None:
        if not self._params.repr:
            return

        flds = [f for f in self._field_list() if f.repr]
        set_new_attribute(self._cls, '__repr__', repr_fn(flds, self._globals))

    def _process_eq(self) -> None:
        if not self._params.eq:
            return

        # flds = [f for f in self._field_list() if f.compare]
        # self_tuple = tuple_str('self', flds)
        # other_tuple = tuple_str('other', flds)
        # set_new_attribute(cls, '__eq__', _cmp_fn('__eq__', '==', self_tuple, other_tuple, globals=globals))
        cmp_fields = (field for field in self._field_list() if field.compare)
        terms = [f'self.{field.name} == other.{field.name}' for field in cmp_fields]
        field_comparisons = ' and '.join(terms) or 'True'
        body = [
            f'if self is other:',
            f' return True',
            f'if other.__class__ is self.__class__:',
            f' return {field_comparisons}',
            f'return NotImplemented',
        ]
        func = create_fn('__eq__', ('self', 'other'), body, globals=self._globals)
        set_new_attribute(self._cls, '__eq__', func)

    def _process_order(self) -> None:
        if not self._params.order:
            return

        flds = [f for f in self._field_list() if f.compare]
        self_tuple = tuple_str('self', flds)
        other_tuple = tuple_str('other', flds)
        for name, op in [
            ('__lt__', '<'),
            ('__le__', '<='),
            ('__gt__', '>'),
            ('__ge__', '>='),
        ]:
            if set_new_attribute(self._cls, name, cmp_fn(name, op, self_tuple, other_tuple, globals=self._globals)):
                raise TypeError(
                    f'Cannot overwrite attribute {name} in class {self._cls.__name__}. '
                    f'Consider using functools.total_ordering'
                )

    def _process_frozen(self) -> None:
        if not self._params.frozen:
            return

        for fn in frozen_get_del_attr(self._cls, self._field_list(), self._globals):
            if set_new_attribute(self._cls, fn.__name__, fn):
                raise TypeError(f'Cannot overwrite attribute {fn.__name__} in class {self._cls.__name__}')

    def _process_hash(self) -> None:
        class_hash = self._cls.__dict__.get('__hash__', dc.MISSING)
        has_explicit_hash = not (class_hash is dc.MISSING or (class_hash is None and '__eq__' in self._cls.__dict__))

        hash_action = HASH_ACTIONS[(
            bool(self._params.unsafe_hash),
            bool(self._params.eq),
            bool(self._params.frozen),
            has_explicit_hash,
        )]
        if hash_action:
            self._cls.__hash__ = hash_action(self._cls, self._field_list(), self._globals)  # type: ignore

    def _process_doc(self) -> None:
        if getattr(self._cls, '__doc__'):
            return

        try:
            text_sig = str(inspect.signature(self._cls)).replace(' -> None', '')
        except (TypeError, ValueError):
            text_sig = ''
        self._cls.__doc__ = (self._cls.__name__ + text_sig)

    def _process_match_args(self) -> None:
        if not self._params12.match_args:
            return

        ifs = get_init_fields(self._fields().values())
        set_new_attribute(self._cls, '__match_args__', tuple(f.name for f in ifs.std))

    def _process_replace(self) -> None:
        set_new_attribute(self._cls, '__replace__', _replace)

    @lang.cached_nullary
    def _transform_slots(self) -> None:
        if self._params12.weakref_slot and not self._params12.slots:
            raise TypeError('weakref_slot is True but slots is False')
        if not self._params12.slots:
            return
        self._cls = add_slots(self._cls, self._params.frozen, self._params12.weakref_slot)

    @lang.cached_nullary
    def process(self) -> type:
        self._check_params()
        self._check_frozen_bases()

        self._process_fields()
        setattr(self._cls, FIELDS_ATTR, self._fields())

        self._process_init()
        self._process_overrides()
        self._process_repr()
        self._process_eq()
        self._process_order()
        self._process_frozen()
        self._process_hash()
        self._process_doc()
        self._process_match_args()
        self._process_replace()

        self._transform_slots()

        abc.update_abstractmethods(self._cls)  # noqa

        return self._cls


def process_class(cls: type) -> type:
    return ClassProcessor(cls).process()
