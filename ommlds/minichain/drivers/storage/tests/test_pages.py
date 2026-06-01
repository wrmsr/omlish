import typing as ta
import uuid

import pytest

from ....chat.messages import Chat
from ....chat.messages import Message
from ....chat.messages import UserMessage
from ....chat.metadata import MessageUuid
from ..impl import make_chat_page_after
from ..impl import make_chat_page_before
from ..impl import make_chat_page_latest
from ..manager import DriverStorageManager
from ..types import ChatPage


class InMemoryDriverStorageManager(DriverStorageManager):
    def __init__(self, chat: Chat = ()) -> None:
        super().__init__()

        self._chat: list[Message] = list(chat)

    def _sequenced_messages(self) -> ta.Sequence[tuple[int, Message]]:
        return tuple(
            (i + 1, message)
            for i, message in enumerate(self._chat)
        )

    async def get_chat(self) -> Chat:
        return tuple(self._chat)

    async def get_latest_chat_page(self, limit: int) -> ChatPage:
        return make_chat_page_latest(
            self._sequenced_messages(),
            limit,
        )

    async def get_chat_page_before(self, seq: int, limit: int) -> ChatPage:
        return make_chat_page_before(
            self._sequenced_messages(),
            seq,
            limit,
        )

    async def get_chat_page_after(self, seq: int, limit: int) -> ChatPage:
        return make_chat_page_after(
            self._sequenced_messages(),
            seq,
            limit,
        )

    async def extend_chat(self, chat_additions: Chat) -> None:
        self._chat.extend(chat_additions)


def _message(s: str) -> UserMessage:
    return UserMessage(s).with_metadata(MessageUuid(uuid.uuid7()))


@pytest.mark.asyncs('asyncio')
async def test_latest_chat_page() -> None:
    messages = [_message(str(i)) for i in range(5)]
    storage = InMemoryDriverStorageManager(messages)

    page = await storage.get_latest_chat_page(2)

    assert page.messages == tuple(messages[-2:])
    assert page.has_before
    assert not page.has_after
    assert page.before_seq == 4
    assert page.after_seq == 5


@pytest.mark.asyncs('asyncio')
async def test_latest_chat_page_with_large_limit() -> None:
    messages = [_message(str(i)) for i in range(3)]
    storage = InMemoryDriverStorageManager(messages)

    page = await storage.get_latest_chat_page(10)

    assert page.messages == tuple(messages)
    assert not page.has_before
    assert not page.has_after
    assert page.before_seq == 1
    assert page.after_seq == 3


@pytest.mark.asyncs('asyncio')
async def test_latest_chat_page_empty() -> None:
    storage = InMemoryDriverStorageManager()

    page = await storage.get_latest_chat_page(10)

    assert page.messages == ()
    assert not page.has_before
    assert not page.has_after
    assert page.before_seq is None
    assert page.after_seq is None


@pytest.mark.asyncs('asyncio')
async def test_chat_page_before() -> None:
    messages = [_message(str(i)) for i in range(6)]
    storage = InMemoryDriverStorageManager(messages)

    page = await storage.get_chat_page_before(5, 2)

    assert page.messages == tuple(messages[2:4])
    assert page.has_before
    assert page.has_after
    assert page.before_seq == 3
    assert page.after_seq == 4


@pytest.mark.asyncs('asyncio')
async def test_chat_page_after() -> None:
    messages = [_message(str(i)) for i in range(6)]
    storage = InMemoryDriverStorageManager(messages)

    page = await storage.get_chat_page_after(2, 3)

    assert page.messages == tuple(messages[2:5])
    assert page.has_before
    assert page.has_after
    assert page.before_seq == 3
    assert page.after_seq == 5


@pytest.mark.asyncs('asyncio')
async def test_chat_page_after_end() -> None:
    messages = [_message(str(i)) for i in range(3)]
    storage = InMemoryDriverStorageManager(messages)

    page = await storage.get_chat_page_after(3, 3)

    assert page.messages == ()
    assert page.has_before
    assert not page.has_after
    assert page.before_seq is None
    assert page.after_seq is None


@pytest.mark.asyncs('asyncio')
async def test_extend_chat_affects_pages() -> None:
    storage = InMemoryDriverStorageManager([_message('0')])

    added = [_message('1'), _message('2')]
    await storage.extend_chat(added)

    page = await storage.get_latest_chat_page(2)

    assert page.messages == tuple(added)
    assert page.has_before
    assert not page.has_after
    assert page.before_seq == 2
    assert page.after_seq == 3
