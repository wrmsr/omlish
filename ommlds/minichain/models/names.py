# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish import cached
from omlish import dataclasses as dc
from omlish.algorithm.toposort import mut_toposort


##


@dc.dataclass(frozen=True, kw_only=True)
class ModelNameCollection:
    default: ta.Optional[str] = None  # noqa

    aliases: ta.Optional[ta.Mapping[str, str]] = None  # noqa

    @cached.property
    def alias_map(self) -> ta.Mapping[str, str]:
        if not (src := self.aliases):
            return {}

        dct: dict[str, str] = {}
        for ks in mut_toposort({k: {v} for k, v in src.items()}):
            for k in ks:
                dct[k] = dct.get(src.get(k, k), k)
        return dct

    @cached.property
    def roots(self) -> frozenset[str]:
        return frozenset(self.alias_map.values())

    def resolve(self, name: str) -> str:
        return self.alias_map.get(name, name)

    @cached.property
    def resolved_default(self) -> str | None:
        if self.default is not None:
            return self.resolve(self.default)
        else:
            return None
