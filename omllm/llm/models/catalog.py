import typing as ta

from omcore import check

from ..types.models import Model
from ..types.models import ModelKey


##


class ModelCatalog(ta.Sequence[Model]):
    def __init__(
            self,
            models: ta.Iterable[Model],
    ) -> None:
        super().__init__()

        lst: list[Model] = []
        by_key: dict[ModelKey, Model] = {}
        for m in models:
            check.not_in(m.key, by_key)
            lst.append(m)
            by_key[m.key] = m

        self._seq = lst
        self._by_key = by_key

    @property
    def seq(self) -> ta.Sequence[Model]:
        return self._seq

    @property
    def by_key(self) -> ta.Mapping[ModelKey, Model]:
        return self._by_key

    #

    def __len__(self) -> int:
        return len(self._seq)

    def __iter__(self) -> ta.Iterator[Model]:
        return iter(self._seq)

    def __contains__(self, key: ModelKey) -> bool:  # type: ignore[override]
        return check.isinstance(key, ModelKey) in self._by_key

    @ta.overload
    def __getitem__(self, index: int | ModelKey, /) -> Model: ...

    @ta.overload
    def __getitem__(self, index: slice, /) -> ta.Sequence[Model]: ...

    def __getitem__(self, index, /):
        if isinstance(index, ModelKey):
            return self._by_key[index]
        else:
            return self._seq[index]
