import abc
import typing as ta

from omlish import check
from omlish import lang

from .... import minichain as mc


##


class ChatSessionPrinter(lang.Abstract):
    @abc.abstractmethod
    def print(self, obj: mc.Message | mc.Content) -> None:
        raise NotImplementedError


##


class StringChatSessionPrinter(ChatSessionPrinter):
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
        if s:
            self._str_printer(s)

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
            elif isinstance(obj, mc.ToolExecResultMessage):
                pass
            else:
                raise TypeError(obj)

        elif isinstance(obj, str):
            self._print_str(obj)

        else:
            raise TypeError(obj)
