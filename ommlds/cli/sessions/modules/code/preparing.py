import typing as ta

from ..... import minichain as mc
from ...chat.drivers.types import PlaceholderContentsProvider
from ...chat.drivers.types import ProvidedSystemMessage
from ...chat.drivers.types import SystemMessageProvider


##


class CodeSystemMessageProvider(SystemMessageProvider):
    async def provide_system_messages(self) -> ta.Sequence[ProvidedSystemMessage]:
        from .....minichain.lib.code.prompts import CODE_AGENT_SYSTEM_PROMPT
        return [ProvidedSystemMessage(CODE_AGENT_SYSTEM_PROMPT, priority=-1)]


class CodePlaceholderContentsProvider(PlaceholderContentsProvider):
    async def provide_placeholder_contents(self) -> 'mc.PlaceholderContents':
        from .....minichain.lib.code import prompts
        k = prompts.CodeAgentSystemPromptEnvironmentPlaceholder
        v = prompts.build_code_agent_system_prompt_environment
        return {k: v}  # type: ignore[return-value]
