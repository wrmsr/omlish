import dataclasses as dc

from omlish import lang

from ..api.classes.params import get_class_spec


##


@dc.dataclass(frozen=True, kw_only=True, eq=False)
class MetaclassSpec(lang.Final):
    confer: frozenset[str] = frozenset()

    final_subclasses: bool = False

    abstract_immediate_subclasses: bool = False


DEFAULT_METACLASS_SPEC = MetaclassSpec()


##


def get_metaclass_spec(cls: type) -> MetaclassSpec:
    if (cs := get_class_spec(cls)) is None:
        return DEFAULT_METACLASS_SPEC
    if (md := cs.metadata) is None:
        return DEFAULT_METACLASS_SPEC
    return md.get(MetaclassSpec, DEFAULT_METACLASS_SPEC)
