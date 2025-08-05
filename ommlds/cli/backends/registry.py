import functools
import typing as ta

from ... import minichain as mc
from .catalog import BackendCatalogEntry


##


def registry_backend_catalog_entry(
        service_cls: ta.Any,
        name: str,
        *args: ta.Any,
        **kwargs: ta.Any,
) -> BackendCatalogEntry:
    return BackendCatalogEntry(
        service_cls,
        name,
        functools.partial(mc.registry_of[service_cls].new, name, *args, **kwargs),
    )
