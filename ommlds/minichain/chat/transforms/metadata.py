import datetime
import typing as ta
import uuid

from omlish import dataclasses as dc

from ...metadata import CreatedAt
from ...metadata import Uuid
from ..messages import Message
from .base import MessageTransform


##


@dc.dataclass(frozen=True)
class UuidAddingMessageTransform(MessageTransform):
    uuid_factory: ta.Callable[[], uuid.UUID] = dc.field(default_factory=lambda: uuid.uuid4)

    def transform_message(self, m: Message) -> Message:
        if Uuid not in m.metadata:
            m = m.with_metadata(Uuid(self.uuid_factory()))
        return m


@dc.dataclass(frozen=True)
class CreatedAtAddingMessageTransform(MessageTransform):
    clock: ta.Callable[[], datetime.datetime] = dc.field(default=datetime.datetime.now)

    def transform_message(self, m: Message) -> Message:
        if CreatedAt not in m.metadata:
            m = m.with_metadata(CreatedAt(self.clock()))
        return m
