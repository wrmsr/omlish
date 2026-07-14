import dataclasses as dc

from ... import lang
from ..impl.api.classes.params import get_class_spec
from ..specs import ClassSpec


##


@dc.dataclass(frozen=True, kw_only=True, eq=False)
class MetaclassSpec(lang.Final):
    confer: frozenset[str] = frozenset()

    final_subclasses: bool = False

    abstract_immediate_subclasses: bool = False


DEFAULT_METACLASS_SPEC = MetaclassSpec()


##


def get_metaclass_spec(obj: type | ClassSpec) -> MetaclassSpec:
    cs: ClassSpec
    if isinstance(obj, type):
        if (cs := get_class_spec(obj)) is None:  # type: ignore[assignment]
            return DEFAULT_METACLASS_SPEC

    elif isinstance(obj, ClassSpec):
        cs = obj

    else:
        raise TypeError(obj)

    return cs.get_last_metadata(MetaclassSpec, DEFAULT_METACLASS_SPEC)
