import dataclasses as dc

from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True, eq=False)
class MetaclassSpec(lang.Final):
    confer: frozenset[str] = frozenset()

    final_subclasses: bool = False

    abstract_immediate_subclasses: bool = False


DEFAULT_METACLASS_SPEC = MetaclassSpec()
