import datetime
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang

from ...metadata import CreatedAt
from ..metadata import ToolUseUuid
from ..types import ToolUseResult
from .execution import ToolUseExecution
from .execution import ToolUseExecutor


##


class MetadataAddingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
            clock: ta.Callable[[], datetime.datetime] = lang.utcnow,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._clock = clock

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResult:
        if CreatedAt not in tue.use.metadata:
            tue = dc.replace(tue, use=tue.use.with_metadata(CreatedAt(self._clock())))

        if ToolUseUuid not in tue.use.metadata:
            tue = dc.replace(tue, use=tue.use.with_metadata(ToolUseUuid(uuid.uuid7())))

        tur = await self._wrapped.execute_tool_use(tue)

        if CreatedAt not in tur.metadata:
            tur = tur.with_metadata(CreatedAt(self._clock()))

        return tur
