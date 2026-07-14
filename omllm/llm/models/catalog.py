import typing as ta

from omcore import check

from ..types.models import Model


##


class ModelCatalog(ta.Sequence[Model]):
    def __init__(
            self,
            models: ta.Iterable[Model],
    ) -> None:
        super().__init__()

        lst: list[Model] = []
        by_id: dict[str, Model] = {}
        for m in models:
            check.not_in(m.id, by_id)
            lst.append(m)
            by_id[m.id] = m

        self._seq = lst
        self._by_id = by_id

    def __len__(self) -> int:
        return len(self._seq)

    def __iter__(self) -> ta.Iterator[Model]:
        return iter(self._seq)

    def __contains__(self, model_id: str) -> bool:  # type: ignore[override]
        return check.isinstance(model_id, str) in self._by_id

    @ta.overload
    def __getitem__(self, index: int | str, /) -> Model: ...

    @ta.overload
    def __getitem__(self, index: slice, /) -> ta.Sequence[Model]: ...

    def __getitem__(self, index, /):
        if isinstance(index, str):
            return self._by_id[index]
        else:
            return self._seq[index]
