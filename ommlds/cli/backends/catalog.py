import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


##


class BackendCatalog(lang.Abstract):
    @abc.abstractmethod
    def get_backend(self, service_cls: ta.Any, name: str) -> ta.Any:
        raise NotImplementedError


##


@dc.dataclass(frozen=True, eq=False)
class BackendCatalogEntry:
    service_cls: ta.Any
    name: str
    factory_fn: ta.Callable[..., ta.Any]


BackendCatalogEntries = ta.NewType('BackendCatalogEntries', ta.Sequence[BackendCatalogEntry])


##


class SimpleBackendCatalog(BackendCatalog):
    def __init__(
            self,
            entries: BackendCatalogEntries,
    ) -> None:
        super().__init__()

        self._entries: list[BackendCatalogEntry] = list(entries)

        dct: dict[ta.Any, dict[str, BackendCatalogEntry]] = {}
        for e in self._entries:
            sc_dct = dct.setdefault(e.service_cls, {})
            check.not_in(e.name, sc_dct)
            sc_dct[e.name] = e
        self._dct = dct

    def get_backend(self, service_cls: ta.Any, name: str) -> ta.Any:
        e = self._dct[service_cls][name]
        return e.factory_fn()
