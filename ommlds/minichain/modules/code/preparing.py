"""
TODO:
 - lol
"""
import functools
import typing as ta

from ...drivers.preparing.types import PlaceholderContents
from ...drivers.preparing.types import PlaceholderContentsProvider
from ...drivers.preparing.types import ProvidedSystemMessage
from ...drivers.preparing.types import SystemMessageProvider
from ...fs import FsRoot
from .prompts import CODE_AGENT_SYSTEM_PROMPT
from .prompts import CodeAgentSystemPromptEnvironmentPlaceholder
from .prompts import build_code_agent_system_prompt_environment


##


class CodeSystemMessageProvider(SystemMessageProvider):
    async def provide_system_messages(self) -> ta.Sequence[ProvidedSystemMessage]:
        return [ProvidedSystemMessage(CODE_AGENT_SYSTEM_PROMPT, priority=-1)]


class CodePlaceholderContentsProvider(PlaceholderContentsProvider):
    def __init__(
            self,
            *,
            fs_root: FsRoot | None = None,
    ) -> None:
        super().__init__()

        self._fs_root = fs_root

    async def provide_placeholder_contents(self) -> PlaceholderContents:
        k = CodeAgentSystemPromptEnvironmentPlaceholder
        v = functools.partial(
            build_code_agent_system_prompt_environment,
            fs_root=self._fs_root,
        )
        return {k: v}  # type: ignore[return-value]
