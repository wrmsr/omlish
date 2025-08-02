import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.formats import json
from ommlds import minichain as mc


if ta.TYPE_CHECKING:
    from omdev import ptk
else:
    ptk = lang.proxy_import('omdev.ptk')


##


class ToolExecutionRequestDeniedError(Exception):
    pass


@dc.dataclass(frozen=True)
class ConfirmingToolExecutor(mc.ToolExecutor):
    inner: mc.ToolExecutor

    @ta.override
    def execute_tool(
            self,
            ctx: mc.ToolContext,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> str:
        tr_dct = dict(
            name=name,
            args=args,
        )
        cr = ptk.strict_confirm(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}\n\n')

        if not cr:
            raise ToolExecutionRequestDeniedError

        return self.inner.execute_tool(
            ctx,
            name,
            args,
        )
