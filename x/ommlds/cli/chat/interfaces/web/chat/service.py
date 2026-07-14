import contextlib
import typing as ta

from omcore import check

from ...... import minichain as mc


##


class ServiceChatStreamer:
    async def __call__(self, chat: mc.Chat) -> ta.AsyncContextManager[ta.AsyncIterator[mc.AiDelta]]:
        @contextlib.asynccontextmanager
        async def outer() -> ta.Any:
            llm = mc.registry_new(mc.ChatChoicesStreamService, 'openai')

            # FIXME: leaks obviously lol, see omcore/resources/managers.py toplevel todo's
            async with (await llm.invoke(mc.ChatChoicesStreamRequest(chat))).v as st_resp:
                async def inner() -> ta.Any:
                    async for o in st_resp:
                        deltas = check.single(o.choices).deltas
                        for delta in deltas:
                            yield delta

                yield inner()

        return outer()
