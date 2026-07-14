import uuid

import pytest

from omcore import orm

from ....chat.messages import UserMessage
from ....chat.metadata import MessageUuid
from ...orm.impl import OrmImpl
from ...types import DriverId
from ..impl import DriverStorageManagerImpl
from ..models import storage_mappers
from ..types import ChatId
from ..types import ChatPage


def _storage_manager_impl() -> DriverStorageManagerImpl:
    return DriverStorageManagerImpl(
        driver_id=DriverId(uuid.uuid7()),
        chat_id=ChatId(uuid.uuid7()),
        orm_=OrmImpl(
            registry=orm.registry(*storage_mappers()),
            store=orm.InMemoryStore(),
        ),
    )


def _message(s: str) -> UserMessage:
    return UserMessage(s).with_metadata(MessageUuid(uuid.uuid7()))


async def _populated_storage(*messages: UserMessage) -> DriverStorageManagerImpl:
    storage = _storage_manager_impl()
    await storage.extend_chat(messages)
    return storage


def _page_contents(page: ChatPage) -> list:
    return [(r.seq, r.message.c) for r in page.rows]  # type: ignore[attr-defined]


@pytest.mark.asyncs('asyncio')
async def test_latest_chat_page() -> None:
    messages = [_message(str(i)) for i in range(5)]
    storage = await _populated_storage(*messages)

    page = await storage.get_latest_chat_page(2)

    assert _page_contents(page) == [(4, '3'), (5, '4')]
    assert page.has_before
    assert not page.has_after
    assert page.first_seq == 4
    assert page.last_seq == 5


@pytest.mark.asyncs('asyncio')
async def test_latest_chat_page_with_large_limit() -> None:
    messages = [_message(str(i)) for i in range(3)]
    storage = await _populated_storage(*messages)

    page = await storage.get_latest_chat_page(10)

    assert _page_contents(page) == [(1, '0'), (2, '1'), (3, '2')]
    assert not page.has_before
    assert not page.has_after


@pytest.mark.asyncs('asyncio')
async def test_latest_chat_page_empty() -> None:
    storage = _storage_manager_impl()

    page = await storage.get_latest_chat_page(10)

    assert page.rows == ()
    assert not page.has_before
    assert not page.has_after
    assert page.first_seq is None
    assert page.last_seq is None


@pytest.mark.asyncs('asyncio')
async def test_chat_page_before() -> None:
    messages = [_message(str(i)) for i in range(6)]
    storage = await _populated_storage(*messages)

    page = await storage.get_chat_page_before(5, 2)

    assert _page_contents(page) == [(3, '2'), (4, '3')]
    assert page.has_before
    assert page.has_after


@pytest.mark.asyncs('asyncio')
async def test_chat_page_after() -> None:
    messages = [_message(str(i)) for i in range(6)]
    storage = await _populated_storage(*messages)

    page = await storage.get_chat_page_after(2, 3)

    assert _page_contents(page) == [(3, '2'), (4, '3'), (5, '4')]
    assert page.has_before
    assert page.has_after


@pytest.mark.asyncs('asyncio')
async def test_chat_page_after_end() -> None:
    messages = [_message(str(i)) for i in range(3)]
    storage = await _populated_storage(*messages)

    page = await storage.get_chat_page_after(3, 3)

    assert page.rows == ()
    assert page.has_before
    assert not page.has_after


@pytest.mark.asyncs('asyncio')
async def test_extend_chat_affects_pages() -> None:
    storage = await _populated_storage(_message('0'))

    added = [_message('1'), _message('2')]
    await storage.extend_chat(added)

    page = await storage.get_latest_chat_page(2)

    assert _page_contents(page) == [(2, '1'), (3, '2')]
    assert page.has_before
    assert not page.has_after
