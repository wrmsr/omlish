import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from ommlds import minichain as mc

if ta.TYPE_CHECKING:
    from omdev import ptk
    from omdev.ptk import markdown as ptk_md

else:
    ptk = lang.proxy_import('omdev.ptk')
    ptk_md = lang.proxy_import('omdev.ptk.markdown')


##


@dc.dataclass(frozen=True)
class PrintingChatService(mc.AbstractChatService):
    inner: mc.ChatService

    def invoke(self, request: mc.ChatRequest) -> mc.ChatResponse:
        resp = self.inner.invoke(request)
        if resp.v.c is not None:
            print(resp.v.c, flush=True)
        return resp


##


@dc.dataclass(frozen=True)
class MarkdownPrintingChatService(mc.AbstractChatService):
    inner: mc.ChatService

    def invoke(self, request: mc.ChatRequest) -> mc.ChatResponse:
        resp = self.inner.invoke(request)
        if isinstance(resp.v, mc.AiMessage) and isinstance(resp.v.c, str):
            ptk.print_formatted_text(
                ptk_md.Markdown(resp.v.c),
                style=ptk.Style(list(ptk_md.MARKDOWN_STYLE)),
            )
        return resp


##


class PrintingChatChoicesStreamService(
    mc.WrappedStreamService[
        mc.ChatChoicesStreamRequest,
        mc.AiChoices,
        mc.ChatChoicesOutputs,
        mc.ChatChoicesStreamOutputs,
    ],
):
    def _process_vs(self, choices_it: ta.Iterator[mc.AiChoices]) -> ta.Iterator[mc.AiChoices]:
        for choices in choices_it:
            c = check.single(choices)
            if c.m.c is not None:
                print(c.m.c, end='', flush=True)
            yield choices
        print(flush=True)
