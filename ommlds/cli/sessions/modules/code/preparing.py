import typing as ta

from ..... import minichain as mc


##


class CodeSystemMessageProvider(mc.drivers.SystemMessageProvider):
    async def provide_system_messages(self) -> ta.Sequence[mc.drivers.ProvidedSystemMessage]:
        from .....minichain.lib.code.prompts import CODE_AGENT_SYSTEM_PROMPT
        return [mc.drivers.ProvidedSystemMessage(CODE_AGENT_SYSTEM_PROMPT, priority=-1)]


class CodePlaceholderContentsProvider(mc.drivers.PlaceholderContentsProvider):
    async def provide_placeholder_contents(self) -> 'mc.PlaceholderContents':
        from .....minichain.lib.code import prompts
        k = prompts.CodeAgentSystemPromptEnvironmentPlaceholder
        v = prompts.build_code_agent_system_prompt_environment
        return {k: v}  # type: ignore[return-value]
