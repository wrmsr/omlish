import functools
import typing as ta

from omlish import check
from omlish import dataclasses as dc

from ...registries.globals import registry_of
from .base import BackendCatalog


##


@dc.dataclass(frozen=True, eq=False)
class SimpleBackendCatalogEntry:
    service_cls: ta.Any
    name: str
    factory_fn: ta.Callable[..., ta.Any]


SimpleBackendCatalogEntries = ta.NewType('SimpleBackendCatalogEntries', ta.Sequence[SimpleBackendCatalogEntry])


##


class SimpleBackendCatalog(BackendCatalog):
    def __init__(
            self,
            entries: SimpleBackendCatalogEntries,
    ) -> None:
        super().__init__()

        self._entries: list[SimpleBackendCatalogEntry] = list(entries)

        dct: dict[ta.Any, dict[str, SimpleBackendCatalogEntry]] = {}
        for e in self._entries:
            sc_dct = dct.setdefault(e.service_cls, {})
            check.not_in(e.name, sc_dct)
            sc_dct[e.name] = e
        self._dct = dct

    def get_backend(self, service_cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> BackendCatalog.Backend:
        e = self._dct[service_cls][name]
        return BackendCatalog.Backend(e.factory_fn, None)


##


def simple_backend_catalog_entry(
        service_cls: ta.Any,
        name: str,
        *args: ta.Any,
        **kwargs: ta.Any,
) -> SimpleBackendCatalogEntry:
    return SimpleBackendCatalogEntry(
        service_cls,
        name,
        functools.partial(registry_of[service_cls].new, name, *args, **kwargs),
    )
