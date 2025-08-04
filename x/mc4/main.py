"""
TODO:
 - streaming printing
  - streaming markdown printing
 - fatter state storage
 - multifns?
"""
import contextlib
import typing as ta

from omdev.home.secrets import install_env_secrets
from omlish import lang
from ommlds import minichain as mc
from ommlds.cli.tools.tools import WEATHER_TOOL

from .completion.base import ChatCompleter
from .completion.services import ChatServiceChatCompleter
from .completion.tools import ToolExecutingChatCompleter
from .driver import ChatDriver
from .management.base import ChatManager
from .management.interactive import InteractiveChatManager
from .management.singleshot import SingleShotChatManager
from .services.optionsadding import OptionsAddingService
from .services.printing import PrintingChatChoicesStreamService
from .services.printing import PrintingChatService
from .tools.confirming import ConfirmingToolExecutor


##


def _main_(
        es: contextlib.ExitStack,
        *,
        prompt: str | None = None,
        backend: str = 'openai',
        stream: bool = False,
        print_output: bool = True,
        tool_map: mc.ToolCatalogEntries | None = None,
        confirm_tool_execution: bool = True,
) -> None:
    install_env_secrets(
        'openai_api_key',
    )

    #

    cm: ChatManager

    if prompt is not None:
        cm = SingleShotChatManager(
            [mc.UserMessage(prompt)],
        )

    else:
        cm = InteractiveChatManager()

    #

    cs_args: list[ta.Any] = [backend]

    cs: mc.ChatService

    if stream:
        ccss: mc.ChatChoicesStreamService = es.enter_context(lang.maybe_managing(  # noqa
            mc.registry_of[mc.ChatChoicesStreamService].new(*cs_args),
        ))

        if print_output:
            ccss = PrintingChatChoicesStreamService(
                ccss,
            )

        cs = mc.ChatChoicesServiceChatService(
            mc.ChatChoicesStreamServiceChatChoicesService(
                ccss,
            ),
        )

    else:
        ccs: mc.ChatChoicesService = es.enter_context(lang.maybe_managing(  # noqa
            mc.registry_of[mc.ChatChoicesService].new(*cs_args),
        ))

        cs = mc.ChatChoicesServiceChatService(
            ccs,
        )

        if print_output:
            cs = PrintingChatService(
                cs,
            )

    if tool_map is not None:
        cs = OptionsAddingService(
            cs,
            [mc.Tool(t.spec) for t in tool_map],
        )

    #

    cc: ChatCompleter = ChatServiceChatCompleter(
        cs,
    )

    if tool_map is not None:
        te: mc.ToolExecutor = mc.ToolCatalog(
            tool_map,
        )

        if confirm_tool_execution:
            te = ConfirmingToolExecutor(
                te,
            )

        cc = ToolExecutingChatCompleter(
            cc,
            te,
        )

    #

    cd = ChatDriver(
        cm,
        cc,
    )

    cd.drive()


def _main(**kwargs: ta.Any) -> None:
    with contextlib.ExitStack() as es:
        _main_(es, **kwargs)


##


def _default_tool_map() -> mc.ToolCatalogEntries:
    return mc.ToolCatalogEntries([
        WEATHER_TOOL,
    ])


_DEFAULT_KWARGS = dict(
    prompt='What is the weather in SF?',
    # backend='tinygrad_llama3',
    # stream=True,
    tool_map=_default_tool_map(),
)


if __name__ == '__main__':
    _main(**_DEFAULT_KWARGS)
