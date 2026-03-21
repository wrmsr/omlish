import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish.algorithm.prefixes import MinUniquePrefixNode
from omlish.algorithm.prefixes import build_min_unique_prefix_tree

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

    #

    @lang.cached_property
    def by_digest(self) -> ta.Mapping[str, ToolPermissionRule]:
        return col.make_map((
            (check.inline(d := fh.digest_field_hash(r), len(d) == fh.FIELD_HASH_DIGEST_LEN), r)
            for r in self.rules
        ), strict=True)

    #

    @lang.cached_function
    def _mup(self) -> MinUniquePrefixNode:
        return build_min_unique_prefix_tree(list(self.by_digest))

    MIN_MIN_DIGEST_LEN: ta.ClassVar[int] = 3

    @lang.cached_property
    def min_digest_len(self) -> int:
        return max(self._mup().min_unique_prefix_len, self.MIN_MIN_DIGEST_LEN)

    @lang.cached_property
    def by_min_digest(self) -> ta.Mapping[str, ToolPermissionRule]:
        mdl = self.min_digest_len
        return col.make_map(((k[:mdl], v) for k, v in self.by_digest.items()), strict=True)

    #

    def __len__(self) -> int:
        return len(self.rules)

    def __iter__(self) -> ta.Iterator[ToolPermissionRule]:
        return iter(self.rules)

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
            if (kl := len(key)) < fh.FIELD_HASH_DIGEST_LEN:
                if kl < self.min_digest_len:
                    raise KeyError(key)
                key = self._mup().lookup(key)
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
