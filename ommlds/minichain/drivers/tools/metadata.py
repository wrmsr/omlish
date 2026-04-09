from omlish import check

from ...chat.messages import ToolUseResultMessage
from ...chat.transform.metadata import CreatedAtAddingMessageTransform
from ...chat.transform.metadata import MessageUuidAddingMessageTransform
from ...chat.transform.metadata import OriginalMetadataStrippingMessageTransform
from ...chat.transform.types import CompositeMessageTransform
from .execution import ToolUseExecution
from .execution import ToolUseExecutor


##


class MetadataAddingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResultMessage:
        res = await self._wrapped.execute_tool_use(tue)

        res = check.isinstance(
            check.single(
                CompositeMessageTransform([
                    CreatedAtAddingMessageTransform(),
                    MessageUuidAddingMessageTransform(),
                    OriginalMetadataStrippingMessageTransform(),
                ]).transform(res),
            ),
            ToolUseResultMessage,
        )

        return res
