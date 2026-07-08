import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect2 as rfl


RflTypeT = ta.TypeVar('RflTypeT', bound=rfl.Type)


##


@ta.final
class RegistryTypeName(dc.Box[str], lang.Final):
    pass


#


def get_annotated_registry_type_name(obj: ta.Any) -> str | None:
    rty = rfl.reflect_type(obj)

    if not isinstance(rty, rfl.AnnotatedType):
        return None

    if (rtn := check.opt_single(a for a in rty.metadata if isinstance(a, RegistryTypeName))) is None:
        return None

    return rtn.v


def registry_type_repr(obj: ta.Any) -> str:
    if (rtn := get_annotated_registry_type_name(obj)) is not None:
        return repr(rtn)

    return repr(obj)


#


@ta.overload
def strip_registry_annotations(obj: RflTypeT) -> RflTypeT: ...


@ta.overload
def strip_registry_annotations(obj: ta.Any) -> ta.Any: ...


def strip_registry_annotations(obj):
    rty = rfl.reflect_type(obj)

    if not isinstance(rty, rfl.AnnotatedType):
        return obj

    if not any(a for a in rty.metadata if isinstance(a, RegistryTypeName)):
        return obj

    new_md = [a for a in rty.metadata if not isinstance(a, RegistryTypeName)]
    if not new_md:
        out_rty = rty.item
    else:
        out_rty = rfl.AnnotatedType(rty.item, tuple(new_md))

    if isinstance(obj, rfl.Type):
        return out_rty
    else:
        return rfl.to_runtime_annotation(out_rty)
