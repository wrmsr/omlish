import typing as ta

from .. import check
from .. import lang


##


@ta.final
class Index(lang.Final):
    def __init__(
            self,
            *,
            _fields: ta.Sequence[str],
            _store_name: str | None = None,
    ) -> None:
        super().__init__()

        self._fields = tuple(check.non_empty_str(f) for f in check.not_empty(_fields))
        self._store_name = check.non_empty_str(_store_name) if _store_name is not None else None

        check.unique(self._fields)

    def _with_store_name(self, store_name: str) -> 'Index':
        return Index(
            _fields=self._fields,
            _store_name=store_name,
        )

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}('
            f'{list(self._fields)!r}'
            f"{f', store_name={self._store_name!r})' if self._store_name else ''}"
            f')'
        )

    @property
    def fields(self) -> tuple[str, ...]:
        return self._fields

    @property
    def store_name(self) -> str | None:
        return self._store_name
