"""
The shared harness for timeline tests: a fully-wired scripted driver with a `Timeline` bound into its scope, an event
recorder, and direct access to the live pieces. Everything real - injector, event bus, ORM (in-memory store), tool
catalog - per the no-mocks house testing style.
"""
import asyncio
import contextlib
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import inject as inj

from ....backends.scripted.scripts import ChatScript
from ....chat.messages import UserChat
from ....chat.messages import UserMessage
from ....chat.metadata import MessageUuid
from ....drivers.actions import SendUserMessagesAction
from ....drivers.ai.configs import AiConfig
from ....drivers.configs import DriverConfig
from ....drivers.storage.manager import DriverStorageManager
from ....drivers.storage.types import ChatId
from ....drivers.testing import bind_scripted_driver
from ....drivers.types import Driver
from ....events.injection import event_callbacks
from ....events.types import Event
from ..inject import bind_timeline
from ..manager import TimelineManager
from ..timeline import Timeline


##


def user_message(s: str) -> UserMessage:
    return UserMessage(s).with_metadata(MessageUuid(uuid.uuid7()))


##


class PausingGate:
    """
    A `ChatScriptGate` that parks the scripted stream at selected gate points until resumed - the lock-step lever for
    choreographing test actions (attaching, snapshotting, paging) at exact mid-stream moments. No sleeps, fully
    deterministic: `wait_paused` completes only once the stream is actually parked, at which point every prior
    emission has been fully processed by all event-bus callbacks.
    """

    def __init__(self, pause_at: ta.Callable[[ta.Any], bool]) -> None:
        super().__init__()

        self._pause_at = pause_at

        self._paused: asyncio.Event = asyncio.Event()
        self._resume: asyncio.Event = asyncio.Event()

        self.points: list[ta.Any] = []

    async def __call__(self, pt: ta.Any) -> None:
        self.points.append(pt)

        if not self._pause_at(pt):
            return

        self._paused.set()
        await self._resume.wait()
        self._resume.clear()
        self._paused.clear()

    async def wait_paused(self) -> None:
        await self._paused.wait()

    def resume(self) -> None:
        self._resume.set()


##


@dc.dataclass(frozen=True, kw_only=True)
class TimelineDriverHarness:
    injector: inj.AsyncInjector

    driver: Driver
    storage: DriverStorageManager
    manager: TimelineManager
    timeline: Timeline

    events: list[Event]

    async def send_user_chat(self, chat: UserChat) -> None:
        await self.driver.do_action(SendUserMessagesAction(chat))

    async def send_user_text(self, s: str) -> None:
        await self.send_user_chat([user_message(s)])


@contextlib.asynccontextmanager
async def timeline_driver_harness(
        script: ChatScript,
        *,
        enable_tools: bool = False,
        stream: bool = True,
        chat_id: ChatId | None = None,
        db_file_path: str | None = None,
        extra_elements: ta.Sequence[inj.Elemental] = (),
) -> ta.AsyncGenerator[TimelineDriverHarness]:
    events: list[Event] = []

    async def on_event(event: Event) -> None:
        events.append(event)

    async with inj.create_async_managed_injector(
        bind_scripted_driver(
            script,
            DriverConfig(ai=AiConfig(
                stream=stream,
                enable_tools=enable_tools,
            )),
            chat_id=chat_id,
            db_file_path=db_file_path,
        ),
        bind_timeline(),
        event_callbacks().bind_item(to_const=on_event),
        *extra_elements,
    ) as injector:
        driver = await injector[Driver]

        await driver.start()

        try:
            yield TimelineDriverHarness(
                injector=injector,
                driver=driver,
                storage=await injector[DriverStorageManager],
                manager=await injector[TimelineManager],
                timeline=await injector[Timeline],
                events=events,
            )

        finally:
            await driver.stop()
