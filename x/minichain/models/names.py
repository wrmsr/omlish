"""
TODO:
 - ctor from {real_name: {alias_names}} ?
"""
import typing as ta

from omcore import cached
from omcore import dataclasses as dc
from omcore import lang
from omcore.algorithm.toposort import mut_toposort


##


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class ModelNameCollection:
    default: str | None = None

    aliases: ta.Mapping[str, str | None] | None = None

    @cached.property
    def resolved(self) -> ta.Mapping[str, str]:
        if not (src := self.aliases):
            return {}

        dct: dict[str, str] = {}
        for ks in mut_toposort({k: {v} for k, v in src.items()}):  # type: ignore
            for k in ks:
                if k is None:
                    continue
                dct[k] = dct.get(src.get(k, k), k)  # type: ignore
        return dct

    @cached.property
    def roots(self) -> frozenset[str]:
        return frozenset(self.resolved.values())

    def resolve(self, name: str) -> str:
        return self.resolved.get(name, name)

    @cached.property
    def resolved_default(self) -> str | None:
        if self.default is not None:
            return self.resolve(self.default)
        else:
            return None
