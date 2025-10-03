import abc
import typing as ta

from omlish import check
from omlish import lang
from omlish.formats import json
from omlish.term.confirm import confirm_action

from .... import minichain as mc


##


class ToolExecutionRequestDeniedError(Exception):
    pass


class ToolExecutionConfirmation(lang.Abstract):
    @abc.abstractmethod
    def confirm_tool_execution_or_raise(
            self,
            tr: mc.ToolUse,
            tce: mc.ToolCatalogEntry,
    ) -> ta.Awaitable[None]:
        raise NotImplementedError


class NopToolExecutionConfirmation(ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(
            self,
            tr: mc.ToolUse,
            tce: mc.ToolCatalogEntry,
    ) -> None:
        pass


class AskingToolExecutionConfirmation(ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(
            self,
            tr: mc.ToolUse,
            tce: mc.ToolCatalogEntry,
    ) -> None:
        tr_dct = dict(
            id=tr.id,
            name=tce.spec.name,
            args=tr.args,
            # spec=msh.marshal(tce.spec),
        )
        cr = confirm_action(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}')  # FIXME: async lol

        if not cr:
            raise ToolExecutionRequestDeniedError


##


class ToolUseExecutor(lang.Abstract):
    @abc.abstractmethod
    def execute_tool_use(
            self,
            tr: mc.ToolUse,
            *ctx_items: ta.Any,
    ) -> ta.Awaitable[mc.ToolUseResultMessage]:
        raise NotImplementedError


class ToolUseExecutorImpl(ToolUseExecutor):
    def __init__(
            self,
            *,
            catalog: mc.ToolCatalog,
            confirmation: ToolExecutionConfirmation,
    ) -> None:
        super().__init__()

        self._catalog = catalog
        self._confirmation = confirmation

    async def execute_tool_use(
            self,
            tr: mc.ToolUse,
            *ctx_items: ta.Any,
    ) -> mc.ToolUseResultMessage:
        tce = self._catalog.by_name[check.non_empty_str(tr.name)]

        await self._confirmation.confirm_tool_execution_or_raise(tr, tce)

        return await mc.execute_tool_use(
            mc.ToolContext(
                tr,
                *ctx_items,
            ),
            tce.executor(),
            tr,
        )
