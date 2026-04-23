import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl


RflTypeT = ta.TypeVar('RflTypeT', bound=rfl.Type)


##


@ta.final
class RegistryTypeName(dc.Box[str], lang.Final):
    pass


#


def get_annotated_registry_type_name(obj: ta.Any) -> str | None:
    if isinstance(obj, rfl.Annotated):
        if (rtn := check.opt_single(a for a in obj.md if isinstance(a, RegistryTypeName))) is not None:
            return rtn.v

    elif rfl.is_annotated_type(obj):
        if (rtn := check.opt_single(a for a in rfl.get_annotated_type_metadata(obj) if isinstance(a, RegistryTypeName))) is not None:  # noqa
            return rtn.v

    return None


def registry_type_repr(obj: ta.Any) -> str:
    if (rtn := get_annotated_registry_type_name(obj)) is not None:
        return rtn

    return repr(obj)


#


@ta.overload
def strip_registry_annotations(obj: RflTypeT) -> RflTypeT:
    ...


@ta.overload
def strip_registry_annotations(obj: ta.Any) -> ta.Any:
    ...


def strip_registry_annotations(obj):
    if isinstance(obj, rfl.Annotated):
        return rfl.strip_rfl_annotations_shallow(obj, lambda a: isinstance(a, RegistryTypeName))

    elif rfl.is_annotated_type(obj):
        cls = ta.get_args(obj)[0]
        new_md = [a for a in rfl.get_annotated_type_metadata(obj) if not isinstance(a, RegistryTypeName)]
        if not new_md:
            return cls
        else:
            return ta.Annotated[cls, *new_md]

    return obj
