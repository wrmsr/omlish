import dataclasses as dc
import enum

from omlish.asyncs import anyio as aiu
import anyio.abc
import trio  # noqa

from ..types import Context
from ..types import DoNotRestart
from ..types import Service
from ..types import TerminateSupervisorTree


class FailableService(Service):
    class Message(enum.Enum):
        HAPPY = enum.auto()
        FAIL = enum.auto()
        PANIC = enum.auto()
        HANG = enum.auto()
        USE_STOP_CHAN = enum.auto()
        TERMINATE_TREE = enum.auto()
        DO_NOT_RESTART = enum.auto()

    @dc.dataclass()
    class Controller:
        started: anyio.abc.ObjectReceiveStream[bool]
        take: anyio.abc.ObjectSendStream['FailableService.Message']
        release: anyio.abc.ObjectSendStream[bool]
        stop: anyio.abc.ObjectReceiveStream[bool]

    @classmethod
    def new(cls, name: str) -> tuple['FailableService', 'FailableService.Controller']:
        started_send, started_receive = aiu.split_memory_object_streams(*anyio.create_memory_object_stream[bool]())
        take_send, take_receive = aiu.split_memory_object_streams(*anyio.create_memory_object_stream[FailableService.Message]())  # noqa
        release_send, release_receive = aiu.split_memory_object_streams(*anyio.create_memory_object_stream[bool]())
        stop_send, stop_receive = aiu.split_memory_object_streams(*anyio.create_memory_object_stream[bool](1))
        return cls(
            name,
            started_send,
            take_receive,
            release_receive,
            stop_send,
        ), FailableService.Controller(
            started_receive,
            take_send,
            release_send,
            stop_receive,
        )

    def __init__(
            self,
            name: str,
            started: anyio.abc.ObjectSendStream[bool],
            take: anyio.abc.ObjectReceiveStream[Message],
            release: anyio.abc.ObjectReceiveStream[bool],
            stop: anyio.abc.ObjectSendStream[bool],
    ) -> None:
        super().__init__()

        self._name = name
        self._started = started
        self._take = take
        self._release = release
        self._stop = stop

        self._existing: int = 0
        self._m = anyio.Lock()
        self._running = False

    async def serve(self, ctx: Context) -> Exception | None:
        async with self._m:
            if self._existing != 0:
                # This will produce a fatal runtime error if FailableService is ever started twice.
                raise RuntimeError
            self._existing += 1
            self._running = True

        try:
            async def release_existence():
                async with self._m:
                    self._existing -= 1

            await self._started.send(True)

            use_stop_chan = False

            while True:
                take_m, done_m = await aiu.first(self._take.receive, ctx.done)

                if take_m.present:
                    val = take_m.must()
                    match val:
                        case FailableService.Message.HAPPY:
                            # Do nothing on purpose. Life is good!
                            pass

                        case FailableService.Message.FAIL:
                            await release_existence()
                            if use_stop_chan:
                                await self._stop.send(True)
                            return None

                        case FailableService.Message.PANIC:
                            await release_existence()
                            raise Exception("Panic!")

                        case FailableService.Message.HANG:
                            # or more specifically, "hang until I release you"
                            await self._release.receive()

                        case FailableService.Message.USE_STOP_CHAN:
                            use_stop_chan = True

                        case FailableService.Message.TERMINATE_TREE:
                            return TerminateSupervisorTree()

                        case FailableService.Message.DO_NOT_RESTART:
                            return DoNotRestart()

                        case _:
                            raise TypeError(val)

                if done_m.present:
                    await release_existence()
                    if use_stop_chan:
                        await self._stop.send(True)
                    return ctx.err()

        finally:
            async with self._m:
                self._running = False
