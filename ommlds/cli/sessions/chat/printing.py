import abc
import typing as ta

from omdev.tui import rich
from omlish import check
from omlish import lang
from omlish.formats import json

from .... import minichain as mc


##


class ChatSessionPrinter(lang.Abstract):
    @abc.abstractmethod
    def print(self, obj: mc.Message | mc.Content) -> None:
        raise NotImplementedError


#


class StringChatSessionPrinter(ChatSessionPrinter, lang.Abstract):
    @abc.abstractmethod
    def _print_str(self, s: str) -> None:
        raise NotImplementedError

    def print(self, obj: mc.Message | mc.Content) -> None:
        if obj is None:
            pass

        elif isinstance(obj, mc.Message):
            if isinstance(obj, mc.SystemMessage):
                if obj.c is not None:
                    self._print_str(check.isinstance(obj.c, str))
            elif isinstance(obj, mc.UserMessage):
                if obj.c is not None:
                    self._print_str(check.isinstance(obj.c, str))
            elif isinstance(obj, mc.AiMessage):
                if obj.c is not None:
                    self._print_str(check.isinstance(obj.c, str))
            elif isinstance(obj, mc.ToolUseResultMessage):
                self._print_str(check.isinstance(obj.tur.c, str))
            else:
                raise TypeError(obj)

        elif isinstance(obj, mc.JsonContent):
            self._print_str(json.dumps_pretty(obj.v))

        elif isinstance(obj, str):
            self._print_str(obj)

        else:
            raise TypeError(obj)


#


class SimpleStringChatSessionPrinter(StringChatSessionPrinter):
    def __init__(
            self,
            *,
            str_printer: ta.Callable[[str], None] | None = None,
    ) -> None:
        super().__init__()

        if str_printer is None:
            str_printer = print
        self._str_printer = str_printer

    def _print_str(self, s: str) -> None:
        s = s.strip()
        if not s:
            return

        self._str_printer(s)


#


class MarkdownStringChatSessionPrinter(StringChatSessionPrinter):
    def _print_str(self, s: str) -> None:
        s = s.strip()
        if not s:
            return

        rich.Console().print(rich.Markdown(s))


##


class StreamPrinter(lang.ExitStacked, lang.Abstract):
    @abc.abstractmethod
    def feed(self, s: str) -> None:
        raise NotImplementedError


#


class SimpleStreamPrinter(StreamPrinter):
    def feed(self, s: str) -> None:
        print(s, end='', flush=True)

    def _exit_contexts(self) -> None:
        super()._exit_contexts()
        print(flush=True)


#


class MarkdownStreamPrinter(StreamPrinter):
    def __init__(self) -> None:
        super().__init__()

    def _enter_contexts(self) -> None:
        super()._enter_contexts()
        self._ir: rich.MarkdownLiveStream = self._enter_context(rich.IncrementalMarkdownLiveStream())

    def feed(self, s: str) -> None:
        self._ir.feed(s)
