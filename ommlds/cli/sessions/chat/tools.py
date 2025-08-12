import abc
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from .... import minichain as mc


if ta.TYPE_CHECKING:
    from omdev import ptk
else:
    ptk = lang.proxy_import('omdev.ptk')


##


class ToolExecutionRequestDeniedError(Exception):
    pass


class ToolExecutionConfirmation(lang.Abstract):
    @abc.abstractmethod
    def m_confirm_tool_execution_or_raise(
            self,
            tr: mc.ToolExecRequest,
            tce: mc.ToolCatalogEntry,
    ) -> lang.Maywaitable[None]:
        raise NotImplementedError


class NopToolExecutionConfirmation(ToolExecutionConfirmation):
    @lang.maysync
    async def m_confirm_tool_execution_or_raise(
            self,
            tr: mc.ToolExecRequest,
            tce: mc.ToolCatalogEntry,
    ) -> None:
        pass


class AskingToolExecutionConfirmation(ToolExecutionConfirmation):
    @lang.maysync
    async def m_confirm_tool_execution_or_raise(
            self,
            tr: mc.ToolExecRequest,
            tce: mc.ToolCatalogEntry,
    ) -> None:
        tr_dct = dict(
            id=tr.id,
            spec=msh.marshal(tce.spec),
            args=tr.args,
        )
        cr = await ptk.m_strict_confirm(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}\n\n').m()

        if not cr:
            raise ToolExecutionRequestDeniedError


##


class ToolExecRequestExecutor(lang.Abstract):
    @abc.abstractmethod
    def m_execute_tool_request(self, tr: mc.ToolExecRequest) -> lang.Maywaitable[mc.ToolExecResultMessage]:
        raise NotImplementedError


class ToolExecRequestExecutorImpl(ToolExecRequestExecutor):
    def __init__(
            self,
            *,
            catalog: mc.ToolCatalog,
            confirmation: ToolExecutionConfirmation,
    ) -> None:
        super().__init__()

        self._catalog = catalog
        self._confirmation = confirmation

    @lang.maysync
    async def m_execute_tool_request(self, tr: mc.ToolExecRequest) -> mc.ToolExecResultMessage:
        tce = self._catalog.by_name[check.non_empty_str(tr.name)]

        await self._confirmation.m_confirm_tool_execution_or_raise(tr, tce).m()

        return await mc.m_execute_tool_request(
            mc.ToolContext(),
            tce.executor(),
            tr,
        ).m()
