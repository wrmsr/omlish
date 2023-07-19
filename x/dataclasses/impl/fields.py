import dataclasses as dc
import collections
import types
import typing as ta

from omlish import check
from omlish import lang

from .internals import FieldType
from .internals import is_classvar
from .internals import is_initvar
from .params import ExField
from .params import ex_field
from .utils import Namespace


MISSING = dc.MISSING

EMPTY_METADATA = types.MappingProxyType({})


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
):  # -> dc.Field
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')

    ex = ExField(
        default=lang.just(default) if default is not MISSING else lang.empty(),
        default_factory=lang.just(default_factory) if default_factory is not MISSING else lang.empty(),
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
        kw_only=kw_only if kw_only is not MISSING else None,
    )

    md: ta.Mapping = {ExField: ex}
    if metadata is not None:
        md = collections.ChainMap(md, metadata)

    bf = dc.Field(
        default,
        default_factory,  # noqa
        init,
        repr,
        hash,
        compare,
        md,
        kw_only,  # noqa
    )

    ex.base = bf

    return bf


def preprocess_field(
        cls: type,
        a_name: str,
        a_type: ta.Any,
        default_kw_only: bool,
) -> dc.Field:
    default = getattr(cls, a_name, MISSING)
    if isinstance(default, dc.Field):
        bf = default
    else:
        if isinstance(default, types.MemberDescriptorType):
            default = MISSING
        bf = field(default=default)
    f = ex_field(bf)

    f.name = a_name
    f.type = a_type

    f.field_type = FieldType.INSTANCE

    if is_classvar(cls, f.type):
        f.field_type = FieldType.CLASS
    if is_initvar(cls, f.type):
        f.field_type = FieldType.INIT

    if f.field_type in (FieldType.CLASS, FieldType.INIT):
        if f.default_factory.present:
            raise TypeError(f'field {f.name} cannot have a default factory')

    if f.field_type in (FieldType.INSTANCE, FieldType.INIT):
        if f.kw_only is None:
            f.kw_only = default_kw_only
    else:
        check.arg(f.field_type is FieldType.CLASS)
        if f.kw_only is not None:
            raise TypeError(f'field {f.name} is a ClassVar but specifies kw_only')

    if f.field_type is FieldType.INSTANCE and f.default.present and (d := f.default.must()).__class__.__hash__ is None:
        raise ValueError(f'mutable default {type(d)} for field {f.name} is not allowed: use default_factory')

    bf.name = f.name
    bf.type = f.type
    bf._field_type = f.field_type.value
    bf.kw_only = f.kw_only

    return bf


def fields_in_init_order(fields: ta.Sequence[ExField]) -> ta.Tuple[ta.Sequence[ExField], ta.Sequence[ExField]]:
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
        f: ExField,
        frozen: bool,
        globals: Namespace,
        self_name: str,
        slots: bool,
) -> ta.Optional[str]:
    default_name = f'__dataclass_dflt_{f.name}__'

    if f.default_factory.present:
        if f.init:
            globals[default_name] = f.default_factory.must()
            value = (
                f'{default_name}() '
                f'if {f.name} is __dataclass_HAS_DEFAULT_FACTORY__ '
                f'else {f.name}'
            )
        else:
            globals[default_name] = f.default_factory.must()
            value = f'{default_name}()'

    else:
        if f.init:
            if not f.default.present:
                value = f.name
            elif f.default.present:
                globals[default_name] = f.default.must()
                value = f.name

        else:
            if slots and f.default.present:
                globals[default_name] = f.default.must()
                value = default_name
            else:
                return None

    if f.field_type is FieldType.INIT:
        return None

    return field_assign(frozen, f.name, value, self_name)  # noqa
