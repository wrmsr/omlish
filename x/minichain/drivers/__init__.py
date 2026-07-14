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
        StaticSystemMessageProvider,
        SystemMessageProviders,

        PlaceholderContentsProvider,
        StaticPlaceholderContentsProvider,
        PlaceholderContentsProviders,

        ChatPreparer,
    )

    #

    from .storage.configs import (  # noqa
        StorageConfig,
    )

    from .storage.manager import (  # noqa
        DriverStorageManager,
    )

    from .storage.types import (  # noqa
        ChatId,

        StoredMessage,
        ChatPage,
    )

    #

    from .tools.configs import (  # noqa
        ToolsConfig,
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

    #

    from .actions import (  # noqa
        ActionDriverEvent,

        SendUserMessagesAction,
    )

    from .configs import (  # noqa
        DriverConfig,
    )

    from .types import (  # noqa
        DriverEvent,

        Action,

        DriverId,
        DriverGetter,
        Driver,
    )

    ##

    from . import inject  # noqa
    from . import injection  # noqa
