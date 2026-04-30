import contextlib
import typing as ta

from ...... import minichain as mc


##


class ServiceChatStreamer:
    async def __call__(self, chat: mc.Chat) -> ta.AsyncContextManager[ta.AsyncIterator[mc.AiDelta]]:
        @contextlib.asynccontextmanager
        async def outer() -> ta.Any:
            raise NotImplementedError

            yield  # type: ignore  # noqa

        return outer()
