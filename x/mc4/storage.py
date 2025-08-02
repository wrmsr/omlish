import abc
import os
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json
from ommlds import minichain as mc


##


class ChatStorage(lang.Abstract):
    @abc.abstractmethod
    def load_chat(self) -> mc.Chat | None:
        raise NotImplementedError

    @abc.abstractmethod
    def save_chat(self, chat: mc.Chat | None) -> None:
        raise NotImplementedError


#


class MemoryChatStorage(ChatStorage):
    def __init__(self, initial: mc.Chat | None = None) -> None:
        super().__init__()

        self._chat = initial

    @ta.override
    def load_chat(self) -> mc.Chat | None:
        return self._chat

    @ta.override
    def save_chat(self, chat: mc.Chat | None) -> None:
        self._chat = chat


#


class JsonFileChatStorage(ChatStorage):
    def __init__(self, file_path: str) -> None:
        super().__init__()

        self._file_path = check.non_empty_str(file_path)

    def _read_file(self) -> str | None:
        try:
            with open(self._file_path) as f:
                return f.read()
        except FileNotFoundError:
            return None

    def _write_file(self, txt: str | None) -> None:
        if txt is None:
            os.remove(self._file_path)
        else:
            with open(self._file_path, 'w') as f:
                f.write(txt)

    @ta.override
    def load_chat(self) -> mc.Chat | None:
        if (txt := self._read_file()) is None:
            return None
        return msh.unmarshal(json.loads(txt), mc.Chat)

    @ta.override
    def save_chat(self, chat: mc.Chat | None) -> None:
        if chat is not None:
            self._write_file(json.dumps_pretty(msh.marshal(chat, mc.Chat)))
        else:
            self._write_file(None)
