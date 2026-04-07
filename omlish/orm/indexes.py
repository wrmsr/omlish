import typing as ta

from .. import check
from .. import lang
from .. import typedvalues as tv
from .options import IndexOption


if ta.TYPE_CHECKING:
    from .mappers import Mapper


##


class UniqueIndexOption(tv.UniqueTypedValue, IndexOption):
    pass


class SortedIndexOption(tv.UniqueTypedValue, IndexOption):
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
        self._given_store_name = _store_name
        if _store_name is not None:
            self._store_name = check.non_empty_str(_store_name)
        self._options = tv.TypedValues(*(_options or []))

        check.unique(self._fields)

        self._is_unique = UniqueIndexOption in self._options
        self._is_sorted = SortedIndexOption in self._options

    _store_name: str

    def _with_store_name(self, store_name: str) -> 'Index':
        return Index(
            _fields=self._fields,
            _store_name=store_name,
            _options=self._options,
        )

    def __repr__(self) -> str:
        try:
            sn = self._store_name
        except AttributeError:
            sn = None
        return (
            f'{type(self).__name__}('
            f'{list(self._fields)!r}'
            f"{f', store_name={sn!r})' if sn else ''}"
            f')'
        )

    @property
    def fields(self) -> tuple[str, ...]:
        return self._fields

    @property
    def store_name(self) -> str:
        return self._store_name

    @property
    def options(self) -> tv.TypedValues[IndexOption]:
        return self._options

    #

    @property
    def is_unique(self) -> bool:
        return self._is_unique

    @property
    def is_sorted(self) -> bool:
        return self._is_sorted

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

    ##
    # Set by mapper

    _field_store_names: tuple[str, ...]

    @property
    def field_store_names(self) -> tuple[str, ...]:
        return self._field_store_names
