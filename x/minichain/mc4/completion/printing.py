import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from ommlds import minichain as mc

from .base import ChatCompleter


if ta.TYPE_CHECKING:
    from omdev import ptk
    from omdev.ptk import markdown as ptk_md

else:
    ptk = lang.proxy_import('omdev.ptk')
    ptk_md = lang.proxy_import('omdev.ptk.markdown')


##


@dc.dataclass(frozen=True)
class PrintingChatCompleter(ChatCompleter):
    inner: ChatCompleter

    @ta.override
    def complete_chat(self, chat: mc.Chat) -> mc.Chat:
        new_messages = self.inner.complete_chat(chat)
        print(new_messages)
        return new_messages


##


@dc.dataclass(frozen=True)
class MarkdownPrintingChatCompleter(ChatCompleter):
    inner: ChatCompleter

    @ta.override
    def complete_chat(self, chat: mc.Chat) -> mc.Chat:
        new_messages = self.inner.complete_chat(chat)
        if new_messages:
            lm = new_messages[-1]
            if isinstance(lm, mc.AiMessage) and isinstance(lm.c, str):
                ptk.print_formatted_text(
                    ptk_md.Markdown(lm.c),
                    style=ptk.Style(list(ptk_md.MARKDOWN_STYLE)),
                )
        return new_messages
