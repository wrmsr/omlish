import dataclasses as dc
import collections
import types
import typing as ta

from omlish import lang

from .internals import FieldType
from .params import ExField


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
        default=default if default is not MISSING else lang.empty(),
        default_factory=default_factory if default_factory is not MISSING else lang.empty(),
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
        kw_only=kw_only if kw_only is not MISSING else lang.empty(),
    )

    md: ta.Mapping = {ExField: ex}
    if metadata is not None:
        md = collections.ChainMap(md, metadata)

    return dc.Field(
        default,
        default_factory,  # noqa
        init,
        repr,
        hash,
        compare,
        md,
        kw_only,  # noqa
    )


def preprocess_field(
        cls,
        a_name: str,
        a_type: ta.Any,
        default_kw_only: bool,
) -> ExField:
    default = getattr(cls, a_name, MISSING)
    if isinstance(default, dc.Field):
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
            f._field_type = dc._FIELD_CLASSVAR

    if f._field_type is _FIELD:
        dataclasses = sys.modules[__name__]
        if (
                _is_initvar(a_type, dataclasses)
                or (
                isinstance(f.type, str) and _is_type(f.type, cls, dataclasses, dataclasses.InitVar, _is_initvar))
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
        raise ValueError(
            f'mutable default {type(f.default)} for field {f.name} is not allowed: use default_factory')

    return f
