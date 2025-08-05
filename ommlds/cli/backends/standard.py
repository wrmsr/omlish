import typing as ta

from ... import minichain as mc
from .catalog import BackendCatalogEntry
from .registry import registry_backend_catalog_entry


##


STANDARD_BACKEND_CATALOG_ENTRIES: ta.Sequence[BackendCatalogEntry] = [
    registry_backend_catalog_entry(mc.ChatChoicesService, 'openai'),

    registry_backend_catalog_entry(mc.ChatChoicesStreamService, 'openai'),

    registry_backend_catalog_entry(mc.CompletionService, 'llamacpp'),
    registry_backend_catalog_entry(mc.CompletionService, 'openai'),
    registry_backend_catalog_entry(mc.CompletionService, 'transformers'),

    registry_backend_catalog_entry(mc.EmbeddingService, 'openai'),
    registry_backend_catalog_entry(mc.EmbeddingService, 'stfm'),
]
