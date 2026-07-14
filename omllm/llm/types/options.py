"""
TODO:
 - *already* want typedvalues?
"""
import typing as ta

from omcore import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class Options:
    """All fields must be optional and default to `None`"""

    max_tokens: int | None = None

    #

    @ta.final
    def merge(self, *overrides: Options | None) -> Options:
        kw: dict[str, ta.Any] = {}
        for obj in [self, *overrides]:
            if obj is None:
                continue

            for fld in dc.fields(self):  # noqa
                fv = getattr(obj, fld.name)

                mv = self._merge_field(fld, fv)

                if mv is None:
                    continue

                kw[fld.name] = mv

        if not kw:
            return self
        return Options(**kw)

    def _merge_field(self, fld: dc.Field, value: ta.Any) -> ta.Any:
        return value
