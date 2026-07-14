import contextlib
import typing as ta

from omcore import inject as inj

from ...... import minichain as mc
from ....backends.inject import bind_backend
from ....configs import ChatConfig
from ....drivers.inject import bind_driver


##


class DriverChatStreamer:
    def __init__(
            self,
            *,
            chat_cfg: ChatConfig = ChatConfig(),
            parent_injector: inj.AsyncInjector | None = None,
    ) -> None:
        super().__init__()

        self._chat_cfg = chat_cfg
        self._parent_injector = parent_injector

    async def __call__(self, chat: mc.Chat) -> ta.AsyncContextManager[ta.AsyncIterator[mc.AiDelta]]:
        @contextlib.asynccontextmanager
        async def outer() -> ta.Any:
            async with contextlib.AsyncExitStack() as aes:
                ec = inj.collect_elements(inj.as_elements(
                    inj.bind(contextlib.AsyncExitStack, to_const=aes),

                    bind_driver(self._chat_cfg.driver, chat_cfg=self._chat_cfg),

                    bind_backend(self._chat_cfg),
                ))

                injector = await inj.create_async_injector(ec, parent=self._parent_injector)

                driver = await injector[mc.drivers.Driver]  # noqa

                raise NotImplementedError

                yield  # type: ignore  # noqa

        return outer()
