import dataclasses as dc
import types
import typing as ta

from ... import check as check_
from ... import lang
from .internals import FieldType
from .internals import is_classvar
from .internals import is_initvar
from .params import get_field_extras

if ta.TYPE_CHECKING:
    from . import api
else:
    api = lang.proxy_import('.api', __package__)


MISSING = dc.MISSING


def field_type(f: dc.Field) -> FieldType:
    if (ft := getattr(f, '_field_type')) is not None:
        return FieldType(ft)
    else:
        return FieldType.INSTANCE


def has_default(f: dc.Field) -> bool:
    return not (f.default is MISSING and f.default_factory is MISSING)


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
    f._field_type = ft.value  # type: ignore

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
        locals: dict[str, ta.Any],
        self_name: str,
        slots: bool,
) -> ta.Sequence[str]:
    default_name = f'__dataclass_dflt_{f.name}__'
    fx = get_field_extras(f)

    lines = []

    if fx.coerce is not None:
        cn = f'__dataclass_coerce__{f.name}__'
        locals[cn] = fx.coerce
        lines.append(f'{f.name} = {cn}({f.name})')

    if fx.check is not None:
        cn = f'__dataclass_check__{f.name}__'
        locals[cn] = fx.check
        lines.append(f'if not {cn}({f.name}): raise __dataclass_CheckException__')

    if fx.check_type:
        cn = f'__dataclass_check_type__{f.name}__'
        locals[cn] = f.type
        lines.append(
            f'if not __dataclass_builtins_isinstance__({f.name}, {cn}): '
            f'raise __dataclass_builtins_TypeError__({f.name}, {cn})'
        )

    value: str | None = None
    if f.default_factory is not MISSING:
        if f.init:
            locals[default_name] = f.default_factory
            value = (
                f'{default_name}() '
                f'if {f.name} is __dataclass_HAS_DEFAULT_FACTORY__ '
                f'else {f.name}'
            )
        else:
            locals[default_name] = f.default_factory
            value = f'{default_name}()'

    elif f.init:
        if f.default is MISSING:
            value = f.name
        elif f.default is not MISSING:
            locals[default_name] = f.default
            value = f.name

    else:
        if slots and f.default is not MISSING:
            locals[default_name] = f.default
            value = default_name
        else:
            pass

    if value is not None and field_type(f) is not FieldType.INIT:
        lines.append(field_assign(frozen, f.name, value, self_name, fx.override))  # noqa

    return lines
