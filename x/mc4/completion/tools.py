import typing as ta

from omlish import dataclasses as dc
from omlish.formats import json
from ommlds import minichain as mc

from ..tools.execution import ToolExecutor
from .base import ChatCompleter


##


@dc.dataclass(frozen=True)
class ToolExecutingChatCompleter(ChatCompleter):
    inner: ChatCompleter
    tool_executor: ToolExecutor

    @ta.override
    def complete_chat(self, chat: mc.Chat) -> mc.Chat:
        ret: list[mc.Message] = []
        while True:
            new = self.inner.complete_chat([*chat, *ret])
            if not new:
                break
            ret.extend(new)

            i = 0
            for cur in new:
                if not isinstance(cur, mc.AiMessage) or not cur.tool_exec_requests:
                    continue

                for tr in cur.tool_exec_requests:
                    tool_res = self.tool_executor.execute_tool_request(tr)

                    trm = mc.ToolExecResultMessage(
                        id=tr.id,
                        name=tr.name,
                        c=json.dumps(tool_res),
                    )
                    ret.append(trm)
                    i += 1

            if not i:
                break

        return ret
