import uuid

import pytest

from omlish import orm

from ....chat.messages import UserMessage
from ....chat.metadata import MessageUuid
from ...orm.impl import OrmImpl
from ...types import DriverId
from ..impl import DriverStorageManagerImpl
from ..models import storage_mappers
from ..types import ChatId


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


@pytest.mark.asyncs('asyncio')
async def test_latest_chat_page() -> None:
    messages = [_message(str(i)) for i in range(5)]
    storage = await _populated_storage(*messages)

    page = await storage.get_latest_chat_page(2)

    assert [m.c for m in page.messages] == ['3', '4']  # type: ignore[attr-defined]
    assert page.has_before
    assert not page.has_after
    assert page.before_seq == 4
    assert page.after_seq == 5


@pytest.mark.asyncs('asyncio')
async def test_latest_chat_page_with_large_limit() -> None:
    messages = [_message(str(i)) for i in range(3)]
    storage = await _populated_storage(*messages)

    page = await storage.get_latest_chat_page(10)

    assert [m.c for m in page.messages] == ['0', '1', '2']  # type: ignore[attr-defined]
    assert not page.has_before
    assert not page.has_after
    assert page.before_seq == 1
    assert page.after_seq == 3


@pytest.mark.asyncs('asyncio')
async def test_latest_chat_page_empty() -> None:
    storage = _storage_manager_impl()

    page = await storage.get_latest_chat_page(10)

    assert page.messages == ()
    assert not page.has_before
    assert not page.has_after
    assert page.before_seq is None
    assert page.after_seq is None


@pytest.mark.asyncs('asyncio')
async def test_chat_page_before() -> None:
    messages = [_message(str(i)) for i in range(6)]
    storage = await _populated_storage(*messages)

    page = await storage.get_chat_page_before(5, 2)

    assert [m.c for m in page.messages] == ['2', '3']  # type: ignore[attr-defined]
    assert page.has_before
    assert page.has_after
    assert page.before_seq == 3
    assert page.after_seq == 4


@pytest.mark.asyncs('asyncio')
async def test_chat_page_after() -> None:
    messages = [_message(str(i)) for i in range(6)]
    storage = await _populated_storage(*messages)

    page = await storage.get_chat_page_after(2, 3)

    assert [m.c for m in page.messages] == ['2', '3', '4']  # type: ignore[attr-defined]
    assert page.has_before
    assert page.has_after
    assert page.before_seq == 3
    assert page.after_seq == 5


@pytest.mark.asyncs('asyncio')
async def test_chat_page_after_end() -> None:
    messages = [_message(str(i)) for i in range(3)]
    storage = await _populated_storage(*messages)

    page = await storage.get_chat_page_after(3, 3)

    assert page.messages == ()
    assert page.has_before
    assert not page.has_after
    assert page.before_seq is None
    assert page.after_seq is None


@pytest.mark.asyncs('asyncio')
async def test_extend_chat_affects_pages() -> None:
    storage = await _populated_storage(_message('0'))

    added = [_message('1'), _message('2')]
    await storage.extend_chat(added)

    page = await storage.get_latest_chat_page(2)

    assert [m.c for m in page.messages] == ['1', '2']  # type: ignore[attr-defined]
    assert page.has_before
    assert not page.has_after
    assert page.before_seq == 2
    assert page.after_seq == 3


@pytest.mark.asyncs('asyncio')
async def test_impl_chat_pages_use_orm_queries() -> None:
    messages = [_message(str(i)) for i in range(6)]
    storage = _storage_manager_impl()
    await storage.extend_chat(messages)

    latest = await storage.get_latest_chat_page(2)
    assert [m.c for m in latest.messages] == ['4', '5']  # type: ignore[attr-defined]
    assert latest.has_before
    assert not latest.has_after
    assert latest.before_seq == 5
    assert latest.after_seq == 6

    before = await storage.get_chat_page_before(5, 2)
    assert [m.c for m in before.messages] == ['2', '3']  # type: ignore[attr-defined]
    assert before.has_before
    assert before.has_after
    assert before.before_seq == 3
    assert before.after_seq == 4

    after = await storage.get_chat_page_after(2, 3)
    assert [m.c for m in after.messages] == ['2', '3', '4']  # type: ignore[attr-defined]
    assert after.has_before
    assert after.has_after
    assert after.before_seq == 3
    assert after.after_seq == 5
