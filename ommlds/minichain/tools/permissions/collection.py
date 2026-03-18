import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ... import _fieldhash as fh
from .types import ToolPermissionRule


##


@ta.final
@dc.dataclass(frozen=True)
class ToolPermissionRules(fh.FieldHashable, ta.Sequence[ToolPermissionRule], lang.Final):
    rules: ta.Sequence[ToolPermissionRule] = dc.xfield(coerce=tuple)

    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('rules', (
            fh.FieldHashField('rules', check.isinstance(self.rules, tuple)),
        ))

    def __getitem__(self, index):
        return self.rules[index]

    def __len__(self):
        return len(self.rules)
