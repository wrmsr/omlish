# fmt: off
# ruff: noqa: I001
from omlish import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()):
    ##

    from .ai.configs import (  # noqa
        AiConfig,
    )

    from .ai.services import (  # noqa
        ChatChoicesServiceOptionsProvider,
        ChatChoicesServiceOptionsProviders,

        ChatChoicesServiceAiChatGenerator,
        ChatChoicesStreamServiceStreamAiChatGenerator,
    )

    from .ai.types import (  # noqa
        AiChatGenerator,
        StreamAiChatGenerator,
    )

    #

    from .events.manager import (  # noqa
        EventsManager,
    )

    from .events.types import (  # noqa
        Event,
        EventCallback,
        EventCallbacks,

        UserMessagesEvent,

        AiMessagesEvent,

        AiStreamBeginEvent,
        AiStreamDeltaEvent,
        AiStreamEndEvent,

        ErrorEvent,

        ToolUseEvent,
        ToolUseResultEvent,
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
        ChatPreparer,
    )

    #

    from .state.configs import (  # noqa
        StateConfig,
    )

    from .state.inmemory import (  # noqa
        InMemoryStateManager,
    )

    from .state.types import (  # noqa
        ChatId,

        State,

        StateManager,
    )

    #

    from .tools.configs import (  # noqa
        ToolsConfig,
    )

    from .tools.confirmation import (  # noqa
        ToolExecutionRequestDeniedError,
        ToolExecutionConfirmation,
        AlwaysDenyToolExecutionConfirmation,
        UnsafeAlwaysAllowToolExecutionConfirmation,
    )

    from .tools.execution import (  # noqa
        ToolContextProvider,

        ToolUseExecutor,
    )

    #

    from .user.configs import (  # noqa
        UserConfig,
    )

    #

    from .configs import (  # noqa
        DriverConfig,
    )

    from .types import (  # noqa
        ProvidedSystemMessage,
        SystemMessageProvider,
        SystemMessageProviders,

        PlaceholderContentsProvider,
        PlaceholderContentsProviders,

        DriverId,
        DriverGetter,
        Driver,
    )

    ##

    from . import inject  # noqa
    from . import injection  # noqa
