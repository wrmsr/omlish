from omlish import dataclasses as dc
from omlish import lang

from .completion.base import ChatCompleter
from .management.base import ChatManager


##


@dc.dataclass(frozen=True)
class ChatDriver(lang.Final):
    chat_manager: ChatManager
    chat_completer: ChatCompleter

    def drive(self) -> None:
        while (cc := self.chat_manager.get_chat_to_complete()) is not None:
            self.chat_manager.update_chat(self.chat_completer.complete_chat(cc))
