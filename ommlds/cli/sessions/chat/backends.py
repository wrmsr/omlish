import typing as ta

from .... import minichain as mc
from ...backends.catalog import BackendCatalogEntry
from ...backends.registry import registry_backend_catalog_entry


##


CHAT_BACKEND_CATALOG_ENTRIES: ta.Sequence[BackendCatalogEntry] = [
    registry_backend_catalog_entry(mc.ChatChoicesService, 'openai'),

    registry_backend_catalog_entry(mc.ChatChoicesStreamService, 'openai'),
]
