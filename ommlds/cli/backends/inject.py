import typing as ta

from omlish import inject as inj
from omlish import lang

from .catalog import BackendCatalog
from .catalog import BackendCatalogEntries
from .catalog import BackendCatalogEntry
from .catalog import SimpleBackendCatalog


##


def bind_backends() -> inj.Elements:
    lst: list[inj.Elemental] = [
        inj.set_binder[BackendCatalogEntry](),
        inj.bind(
            lang.typed_lambda(BackendCatalogEntries, s=ta.AbstractSet[BackendCatalogEntry])(
                lambda s: list(s),
            ),
            singleton=True,
        ),

        inj.bind(SimpleBackendCatalog, singleton=True),
        inj.bind(BackendCatalog, to_key=SimpleBackendCatalog),
    ]

    return inj.as_elements(*lst)
