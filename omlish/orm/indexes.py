import typing as ta

from .. import check
from .. import lang
from .. import typedvalues as tv
from .options import IndexOption


if ta.TYPE_CHECKING:
    from .mappers import Mapper


##


class SortedIndexOption(tv.UniqueTypedValue, IndexOption):
    pass


class UniqueIndexOption(tv.UniqueTypedValue, IndexOption):
    pass


class ClusteredIndexOption(tv.UniqueTypedValue, IndexOption):
    pass


##


@ta.final
class Index(lang.Final):
    def __init__(
            self,
            *,
            _fields: ta.Sequence[str],
            _store_name: str | None = None,
            _options: ta.Sequence[IndexOption] | None = None,
    ) -> None:
        super().__init__()

        self._fields = tuple(check.non_empty_str(f) for f in check.not_empty(_fields))
        self._store_name = check.non_empty_str(_store_name) if _store_name is not None else None
        self._options = tv.TypedValues(*(_options or []))

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

    @property
    def options(self) -> tv.TypedValues[IndexOption]:
        return self._options

    #

    _mapper: 'Mapper'

    def _set_mapper(self, r: 'Mapper') -> None:
        try:
            self._mapper  # noqa
        except AttributeError:
            pass
        else:
            raise RuntimeError('mapper already set')
        self._mapper = r

    @property
    def mapper(self) -> 'Mapper':
        return self._mapper
