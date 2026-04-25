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

    from .commands.base import (  # noqa
        CommandError,
        ArgsCommandError,

        Command,

        ParserClassCommand,
    )

    from .commands.manager import (  # noqa
        CommandsManager,
    )

    from .commands.types import (  # noqa
        Commands,
    )

    from .configs import (  # noqa
        FacadeConfig,
    )

    from .input import (  # noqa
        UserInputSender,
    )

    from .text import (  # noqa
        CanFacadeText,
        FacadeTextColor,

        FacadeTextStyle,

        FacadeText,
        StrFacadeText,
        ConcatFacadeText,
        StyleFacadeText,
    )

    from .types import (  # noqa
        Facade,
    )

    from .ui import (  # noqa
        UiMessageDisplayer,
        NopUiMessageDisplayer,
        PrintMessageDisplayer,

        UiQuitSignal,
        raise_system_exit_ui_quit_signal,
    )

    ##

    from . import inject  # noqa
    from . import injection  # noqa
