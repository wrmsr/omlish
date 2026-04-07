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

    from .events.logging import (  # noqa
        EventLogger,
    )

    from .events.manager import (  # noqa
        EventsManager,
    )

    from .events.types import (  # noqa
        EventCallback,
        EventCallbacks,

        ErrorEvent,
    )

    #

    from .orm.configs import (  # noqa
        OrmConfig,
    )

    from .orm.types import (  # noqa
        Orm,
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

    from .state.configs import (  # noqa
        StateConfig,
    )

    from .state.manager import (  # noqa
        DriverStateManager,
    )

    from .state.models import (  # noqa
        DriverChat,
        DriverMessage,
        DriverState,
    )

    from .state.types import (  # noqa
        ChatId,
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


##


from omlish import marshal as _msh  # noqa

_msh.register_global_module_import('._marshal', __package__)
