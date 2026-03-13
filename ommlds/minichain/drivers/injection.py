from omlish import inject as inj
from omlish import lang

from .ai.injection import chat_options_providers  # noqa
from .events.injection import event_callbacks  # noqa
from .phases.injection import phase_callbacks  # noqa
from .tools.injection import ToolSetBinder  # noqa
from .tools.injection import bind_tool_context_provider_to_key  # noqa
from .tools.injection import tool_catalog_entries  # noqa
from .tools.injection import tool_context_providers  # noqa
from .types import PlaceholderContentsProvider
from .types import PlaceholderContentsProviders
from .types import SystemMessageProvider
from .types import SystemMessageProviders


##


@lang.cached_function
def system_message_providers() -> inj.ItemsBinderHelper[SystemMessageProvider]:
    return inj.items_binder_helper[SystemMessageProvider](SystemMessageProviders)


@lang.cached_function
def placeholder_contents_providers() -> inj.ItemsBinderHelper[PlaceholderContentsProvider]:
    return inj.items_binder_helper[PlaceholderContentsProvider](PlaceholderContentsProviders)
