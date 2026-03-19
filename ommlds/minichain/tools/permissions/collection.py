import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

from ... import _fieldhash as fh
from .types import ToolPermissionRule


##


@ta.final
@dc.dataclass(frozen=True)
class ToolPermissionRules(fh.FieldHashable, lang.Final):
    rules: ta.Sequence[ToolPermissionRule] = dc.xfield(coerce=tuple)

    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('rules', (
            fh.FieldHashField('rules', check.isinstance(self.rules, tuple)),
        ))

    def __len__(self) -> int:
        return len(self.rules)

    def __iter__(self) -> ta.Iterator[ToolPermissionRule]:
        return iter(self.rules)

    @lang.cached_property
    def by_digest(self) -> ta.Mapping[str, ToolPermissionRule]:
        return col.make_map(((fh.digest_field_hash(r), r) for r in self.rules), strict=True)

    @ta.overload
    def __getitem__(self, key: int) -> ToolPermissionRule:
        ...

    @ta.overload
    def __getitem__(self, key: slice) -> ta.Sequence[ToolPermissionRule]:
        ...

    @ta.overload
    def __getitem__(self, key: str) -> ToolPermissionRule:
        ...

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self.rules[key]
        elif isinstance(key, str):
            return self.by_digest[key]
        else:
            raise TypeError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.by_digest

    @ta.overload
    def get(self, key: str, default: None = None) -> ToolPermissionRule | None:
        ...

    @ta.overload
    def get(self, key: str, default: ToolPermissionRule) -> ToolPermissionRule:
        ...

    def get(self, key, default=None):
        return self.by_digest.get(key, default)
