"""
TODO:
 - point validate / check exceptions to lambdas
"""
import dataclasses as dc
import types
import typing as ta

from ... import check as check_
from ... import lang
from .exceptions import FieldValidationError
from .internals import FIELDS_ATTR
from .internals import FieldType
from .internals import is_classvar
from .internals import is_initvar
from .internals import is_kw_only
from .params import get_field_extras
from .processing import Processor


if ta.TYPE_CHECKING:
    from . import api
else:
    api = lang.proxy_import('.api', __package__)


MISSING = dc.MISSING


##


def raise_field_validation_error(
        obj: ta.Any,
        field: str,
        fn: ta.Callable,
        value: ta.Any,
) -> ta.NoReturn:
    raise FieldValidationError(
        obj,
        field,
        fn,
        value,
    )


##


def field_type(f: dc.Field) -> FieldType:
    if (ft := getattr(f, '_field_type')) is not None:
        return FieldType(ft)
    else:
        return FieldType.INSTANCE


def has_default(f: dc.Field) -> bool:
    return not (f.default is MISSING and f.default_factory is MISSING)


##


class FieldsProcessor(Processor):
    def _process(self) -> None:
        cls = self._info.cls
        fields: dict[str, dc.Field] = {}

        for b in cls.__mro__[-1:0:-1]:
            base_fields = getattr(b, FIELDS_ATTR, None)
            if base_fields is not None:
                for f in base_fields.values():
                    fields[f.name] = f

        cls_fields: list[dc.Field] = []

        kw_only = self._info.params.kw_only
        kw_only_seen = False
        for name, ann in self._info.cls_annotations.items():
            if is_kw_only(cls, ann):
                if kw_only_seen:
                    raise TypeError(f'{name!r} is KW_ONLY, but KW_ONLY has already been specified')
                kw_only_seen = True
                kw_only = True
            else:
                cls_fields.append(preprocess_field(cls, name, ann, kw_only))

        for f in cls_fields:
            fields[f.name] = f
            if isinstance(getattr(cls, f.name, None), dc.Field):
                if f.default is MISSING:
                    delattr(cls, f.name)
                else:
                    setattr(cls, f.name, f.default)

        for name, value in cls.__dict__.items():
            if isinstance(value, dc.Field) and name not in self._info.cls_annotations:
                raise TypeError(f'{name!r} is a field but has no type annotation')

        setattr(cls, FIELDS_ATTR, fields)


##


def preprocess_field(
        cls: type,
        a_name: str,
        a_type: ta.Any,
        default_kw_only: bool,
) -> dc.Field:
    default = getattr(cls, a_name, MISSING)
    if isinstance(default, dc.Field):
        f = default
    else:
        if isinstance(default, types.MemberDescriptorType):
            # This is a field in __slots__, so it has no default value.
            default = MISSING
        f = api.field(default=default)

    f.name = a_name
    f.type = a_type

    ft = FieldType.INSTANCE
    if is_classvar(cls, f.type):
        ft = FieldType.CLASS
    if is_initvar(cls, f.type):
        ft = FieldType.INIT
    if ft in (FieldType.CLASS, FieldType.INIT):
        if f.default_factory is not MISSING:
            raise TypeError(f'field {f.name} cannot have a default factory')
    f._field_type = ft.value  # type: ignore  # noqa

    if ft in (FieldType.INSTANCE, FieldType.INIT):
        if f.kw_only is MISSING:
            f.kw_only = default_kw_only
    else:
        check_.arg(ft is FieldType.CLASS)
        if f.kw_only is not MISSING:
            raise TypeError(f'field {f.name} is a ClassVar but specifies kw_only')

    if ft is FieldType.INSTANCE and f.default is not MISSING and f.default.__class__.__hash__ is None:
        raise ValueError(f'mutable default {type(f.default)} for field {f.name} is not allowed: use default_factory')

    return f


def field_assign(
        frozen: bool,
        name: str,
        value: ta.Any,
        self_name: str,
        override: bool,
) -> str:
    if override:
        return f'{self_name}.__dict__[{name!r}] = {value}'
    if frozen:
        return f'__dataclass_builtins_object__.__setattr__({self_name}, {name!r}, {value})'
    return f'{self_name}.{name} = {value}'


def field_init(
        f: dc.Field,
        frozen: bool,
        locals: dict[str, ta.Any],  # noqa
        self_name: str,
        slots: bool,
        cls_override: bool,
) -> ta.Sequence[str]:
    default_name = f'__dataclass_dflt_{f.name}__'
    fx = get_field_extras(f)

    lines = []

    value: str | None = None
    if f.default_factory is not MISSING:
        if f.init:
            locals[default_name] = f.default_factory
            lines.append(f'if {f.name} is __dataclass_HAS_DEFAULT_FACTORY__: {f.name} = {default_name}()')
            value = f.name
        else:
            locals[default_name] = f.default_factory
            lines.append(f'{f.name} = {default_name}()')
            value = f.name

    elif f.init:
        if f.default is MISSING:
            value = f.name
        elif f.default is not MISSING:
            locals[default_name] = f.default  # Not referenced her, just useful / consistent to have in function scope
            value = f.name

    elif slots and f.default is not MISSING:
        locals[default_name] = f.default
        lines.append(f'{f.name} = {default_name}')
        value = default_name

    else:
        pass

    if fx.derive is not None:
        raise NotImplementedError

    if fx.frozen:
        raise NotImplementedError

    if fx.coerce is not None:
        cn = f'__dataclass_coerce__{f.name}__'
        locals[cn] = fx.coerce
        lines.append(f'{value} = {cn}({value})')

    if fx.validate is not None:
        cn = f'__dataclass_validate__{f.name}__'
        locals[cn] = fx.validate
        lines.append(
            f'if not {cn}({value}): '
            f'__dataclass_raise_field_validation_error__({self_name}, {f.name!r}, {cn}, {value})',
        )

    if fx.check_type:
        cn = f'__dataclass_check_type__{f.name}__'
        ct: ta.Any
        if isinstance(fx.check_type, tuple):
            ct = tuple(type(None) if e is None else check_.isinstance(e, type) for e in fx.check_type)
        elif isinstance(fx.check_type, (type, tuple)):
            ct = fx.check_type
        # FIXME:
        # elif info.params_extras.generic_init:
        #     ct = info.generic_replaced_field_annotations[f.name]
        else:
            ct = f.type
        locals[cn] = ct
        lines.append(
            f'if not __dataclass_builtins_isinstance__({value}, {cn}): '
            f'raise __dataclass_builtins_TypeError__({value}, {cn})',
        )

    if value is not None and field_type(f) is not FieldType.INIT:
        lines.append(field_assign(
            frozen,
            f.name,
            value,
            self_name,
            fx.override or cls_override,
        ))

    return lines
