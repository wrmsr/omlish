# fmt: off
# ruff: noqa: I001
from omlish import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from omlish import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()):
    ##

    from .ai.configs import (  # noqa
        AiConfig,
    )

    from .ai.events import (  # noqa
        AiMessagesEvent,

        AiStreamEvent,
        AiStreamBeginEvent,
        AiStreamDeltaEvent,
        AiStreamEndEvent,
    )

    from .ai.services import (  # noqa
        ChatChoicesServiceOptionsProvider,
        ChatChoicesServiceOptionsProviders,

        ChatChoicesServiceAiChatGenerator,
        ChatChoicesStreamServiceStreamAiChatGenerator,
    )

    from .ai.types import (  # noqa
        GenerateAiChatArgs,
        AiChatGenerator,
        StreamAiChatGenerator,
    )

    #

    from .events.manager import (  # noqa
        EventsManager,
    )

    from .events.types import (  # noqa
        EventCallback,
        EventCallbacks,

        ErrorEvent,
    )

    #

    from .phases.manager import (  # noqa
        PhaseManager,
    )

    from .phases.types import (  # noqa
        Phase,

        PhaseCallback,
        PhaseCallbacks,
    )

    #

    from .preparing.types import (  # noqa
        ProvidedSystemMessage,
        SystemMessageProvider,
        SystemMessageProviders,

        PlaceholderContentsProvider,
        PlaceholderContentsProviders,

        ChatPreparer,
    )

    #

    from .state.storage.inmemory import (  # noqa
        InMemoryStateStorage,
    )

    from .state.storage.json import (  # noqa
        JsonFileStateStorage,
    )

    from .state.storage.manager import (  # noqa
        DriverStateStorageKey,
        build_driver_storage_key,

        StateStorageDriverStateManager,
    )

    from .state.storage.marshaled import (  # noqa
        MarshaledStateStorage,
    )

    from .state.storage.sql import (  # noqa
        SqlStateStorage,
    )

    from .state.storage.types import (  # noqa
        StateStorage,
    )

    from .state.configs import (  # noqa
        StateConfig,
    )

    from .state.inmemory import (  # noqa
        InMemoryStateManager,
    )

    from .state.manager import (  # noqa
        StateManager,
    )

    from .state.types import (  # noqa
        ChatId,

        State,
    )

    #

    from .tools.configs import (  # noqa
        ToolsConfig,
    )

    from .tools.eventemit import (  # noqa
        ToolUseEvent,
        ToolUseResultEvent,
    )

    from .tools.execution import (  # noqa
        ToolContextProvider,

        ToolUseExecution,
        ToolUseExecutor,
    )

    from .tools.permissions import (  # noqa
        ToolPermissionConfirmation,

        AlwaysDenyToolPermissionConfirmation,
        UnsafeAlwaysAllowToolPermissionConfirmation,

        StandardToolPermissionDecider,
    )

    #

    from .user.configs import (  # noqa
        UserConfig,
    )

    from .user.events import (  # noqa
        UserMessagesEvent,
    )

    #

    from .actions import (  # noqa
        SendUserMessagesAction,
    )

    from .configs import (  # noqa
        DriverConfig,
    )

    from .types import (  # noqa
        Action,

        Event,

        DriverId,
        DriverGetter,
        Driver,
    )

    ##

    from . import inject  # noqa
    from . import injection  # noqa
