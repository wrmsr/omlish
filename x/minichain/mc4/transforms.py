import abc
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from ommlds import minichain as mc


##


class ChatTransform(lang.Abstract):
    @abc.abstractmethod
    def transform_chat(self, chat: mc.Chat) -> mc.Chat:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class MessageUuidAddingChatTransform(ChatTransform):
    uuid_factory: ta.Callable[[], uuid.UUID] = dc.field(default_factory=lambda: uuid.uuid4)

    @ta.override
    def transform_chat(self, chat: mc.Chat) -> mc.Chat:
        return [
            m.with_metadata(mc.Uuid(self.uuid_factory())) if mc.Uuid not in m.metadata else m
            for m in chat
        ]
