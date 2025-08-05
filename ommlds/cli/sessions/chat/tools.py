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


class ToolExecRequestExecutor(lang.Abstract):
    @abc.abstractmethod
    def execute_tool_request(
            self,
            ter: mc.ToolExecRequest,
    ) -> mc.ToolExecResultMessage:
        raise NotImplementedError


##


class ToolExecutionRequestDeniedError(Exception):
    pass


class ToolExecRequestExecutorImpl(ToolExecRequestExecutor):
    def __init__(
            self,
            *,
            tool_catalog: mc.ToolCatalog | None = None,
    ) -> None:
        super().__init__()

        self._tool_catalog = tool_catalog

    def execute_tool_request(self, tr: mc.ToolExecRequest) -> mc.ToolExecResultMessage:
        tce = check.not_none(self._tool_catalog).by_name[check.non_empty_str(tr.name)]

        tr_dct = dict(
            id=tr.id,
            spec=msh.marshal(tce.spec),
            args=tr.args,
        )
        cr = ptk.strict_confirm(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}\n\n')

        if not cr:
            raise ToolExecutionRequestDeniedError

        return mc.execute_tool_request(
            mc.ToolContext(),
            check.not_none(self._tool_catalog),
            tr,
        )
