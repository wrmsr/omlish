import re
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from . import _fieldhash as fh
from .types import ToolPermissionMatcher
from .types import ToolPermissionTarget


##


@ta.final
@dc.dataclass(frozen=True)
class UrlToolPermissionTarget(ToolPermissionTarget, lang.Final):
    url: str

    _: dc.KW_ONLY

    method: str | None = None

    @dc.validate
    def _validate_method(self) -> bool:
        return (m := self.method) is None or (bool(m) and m.isupper())

    @lang.cached_function
    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('url', (
            fh.FieldHashField('url', self.url),
            fh.FieldHashField('method', self.method),
        ))


@ta.final
@dc.dataclass(frozen=True)
class RegexUrlToolPermissionMatcher(ToolPermissionMatcher, lang.Final):
    pat: str

    _: dc.KW_ONLY

    methods: ta.Container[str] | None = dc.xfield(
        default=None,
    ) | dc.with_extra_field_params(
        coerce=lambda v: tuple(sorted({check.non_empty_str(m).upper() for m in v})) if v is not None else None,
    ) | msh.with_field_options(
        omit_if=lang.is_none,
        marshal_as=ta.Sequence[str] | None,
        unmarshal_as=ta.Sequence[str] | None,
    )

    @lang.cached_function
    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('regex_url', (
            fh.FieldHashField('pat', self.pat),
            fh.FieldHashField('methods', check.isinstance(self.methods, tuple) if self.methods is not None else None),
        ))

    @lang.cached_function
    def compiled_pat(self) -> re.Pattern:
        return re.compile(self.pat)

    def match(self, target: ToolPermissionTarget) -> bool:
        if not isinstance(target, UrlToolPermissionTarget):
            return False

        return (
            self.compiled_pat().fullmatch(target.url) is not None and
            (self.methods is None or (target.method is not None and target.method in self.methods))
        )
