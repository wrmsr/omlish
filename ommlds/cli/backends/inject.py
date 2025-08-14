import typing as ta

from omlish import inject as inj
from omlish import lang

from .catalog import BackendCatalog
from .catalog import BackendCatalogEntries
from .catalog import BackendCatalogEntry
from .catalog import SimpleBackendCatalog
from .standard import STANDARD_BACKEND_CATALOG_ENTRIES
from .strings import BackendStringBackendCatalog


##


def bind_backends(
        *,
        enable_backend_strings: bool = False,
) -> inj.Elements:
    lst: list[inj.Elemental] = []

    #

    lst.extend([
        inj.set_binder[BackendCatalogEntry](),
        inj.bind(
            lang.typed_lambda(BackendCatalogEntries, s=ta.AbstractSet[BackendCatalogEntry])(
                lambda s: list(s),
            ),
            singleton=True,
        ),
    ])

    #

    if enable_backend_strings:
        lst.extend([
            inj.bind(BackendStringBackendCatalog, singleton=True),
            inj.bind(BackendCatalog, to_key=BackendStringBackendCatalog),
        ])

    else:
        lst.extend([
            inj.bind(SimpleBackendCatalog, singleton=True),
            inj.bind(BackendCatalog, to_key=SimpleBackendCatalog),
        ])

    #

    lst.extend([
        inj.bind_set_entry_const(ta.AbstractSet[BackendCatalogEntry], e)
        for e in STANDARD_BACKEND_CATALOG_ENTRIES
    ])

    #

    return inj.as_elements(*lst)
