import dataclasses as dc
import collections.abc
import types
import typing as ta

from omlish import check as check_

from .internals import FieldType
from .internals import is_classvar
from .internals import is_initvar
from .params import FieldExtras
from .params import get_field_extras


MISSING = dc.MISSING


def field_type(f: dc.Field) -> FieldType:
    if (ft := getattr(f, '_field_type')) is not None:
        return FieldType(ft)
    else:
        return FieldType.INSTANCE


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

        coerce: ta.Optional[ta.Callable[[ta.Any], ta.Any]] = None,
        check: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
):  # -> dc.Field
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')

    fx = FieldExtras(
        coerce=coerce,
        check=check,
    )

    md: ta.Mapping = {FieldExtras: fx}
    if metadata is not None:
        md = collections.ChainMap(md, check_.isinstance(metadata, collections.abc.Mapping))  # type: ignore

    return dc.Field(
        default,
        default_factory,  # noqa
        init,
        repr,
        hash,
        compare,
        types.MappingProxyType(md),
        kw_only,  # noqa
    )


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
            default = MISSING
        f = field(default=default)

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


def fields_in_init_order(fields: ta.Sequence[dc.Field]) -> ta.Tuple[ta.Sequence[dc.Field], ta.Sequence[dc.Field]]:
    return (
        tuple(f for f in fields if f.init and not f.kw_only),
        tuple(f for f in fields if f.init and f.kw_only),
    )


def field_assign(
        frozen: bool,
        name: str,
        value: ta.Any,
        self_name: str,
) -> str:
    if frozen:
        return f'__dataclass_builtins_object__.__setattr__({self_name},{name!r},{value})'
    return f'{self_name}.{name}={value}'


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
        lines.append(field_assign(frozen, f.name, value, self_name))  # noqa

    return lines
