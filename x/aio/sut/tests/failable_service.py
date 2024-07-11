import dataclasses as dc
import enum

from omlish.asyncs import anyio as aiu
import anyio.abc
import trio  # noqa

from ..types import Context
from ..types import Service


class FailableServiceMessage(enum.Enum):
    HAPPY = enum.auto()
    FAIL = enum.auto()
    PANIC = enum.auto()
    HANG = enum.auto()
    USE_STOP_CHAN = enum.auto()
    TERMINATE_TREE = enum.auto()
    DO_NOT_RESTART = enum.auto()


class FailableService(Service):
    @dc.dataclass()
    class Controller:
        started: anyio.abc.ObjectReceiveStream[bool]
        take: anyio.abc.ObjectSendStream[FailableServiceMessage]
        release: anyio.abc.ObjectReceiveStream[bool]
        stop: anyio.abc.ObjectReceiveStream[bool]

    @classmethod
    def new(cls, name: str) -> tuple['FailableService', 'FailableService.Controller']:
        started_send, started_receive = aiu.split_memory_object_streams(*anyio.create_memory_object_stream[bool](1))
        take_send, take_receive = aiu.split_memory_object_streams(*anyio.create_memory_object_stream[FailableServiceMessage](1))
        release_send, release_receive = aiu.split_memory_object_streams(*anyio.create_memory_object_stream[bool](1))
        stop_send, stop_receive = aiu.split_memory_object_streams(*anyio.create_memory_object_stream[bool](1))
        return cls(
            name,
            started_send,
            take_receive,
            release_send,
            stop_send,
        ), FailableService.Controller(
            started_receive,
            take_send,
            release_receive,
            stop_receive,
        )

    def __init__(
            self,
            name: str,
            started: anyio.abc.ObjectSendStream[bool],
            take: anyio.abc.ObjectReceiveStream[FailableServiceMessage],
            release: anyio.abc.ObjectSendStream[bool],
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

    async def serve(self, ctx: Context) -> None:
        with self._m:
            if self._existing != 0:
                # This will produce a fatal runtime error if FailableService is ever started twice.
                raise RuntimeError
            self._existing += 1
            self._running = True

        try:
            def release_existence():
                with self._m:
                    self._existing -= 1

            await self._started.send(True)

            use_stop_chan = False

            while True:
                # select {
                # case val := <-self._take:
                #     switch val {
                #     case HAPPY:
                #         // Do nothing on purpose. Life is good!
                #     case FAIL:
                #         releaseExistence()
                #         if useStopChan {
                #             self._stop <- true
                #         }
                #         return nil
                #     case PANIC:
                #         releaseExistence()
                #         panic("Panic!")
                #     case HANG:
                #         // or more specifically, "hang until I release you"
                #         <-self._release
                #     case USE_STOP_CHAN:
                #         useStopChan = true
                #     case TERMINATE_TREE:
                #         return ErrTerminateSupervisorTree
                #     case DO_NOT_RESTART:
                #         return ErrDoNotRestart
                #     }
                # case <-ctx.Done():
                #     releaseExistence()
                #     if useStopChan {
                #         self._stop <- true
                #     }
                #     return ctx.Err()
                pass

        finally:
            with self._m:
                self._running = False
