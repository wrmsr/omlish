import contextlib
import typing as ta

from omlish import check
from omlish import inject as inj
from omlish import lang

from ....configs import ChatConfig
from ._inject import bind_driver_internal
from .interface import ChatDriverInterface


##


class DriverManager(lang.AsyncContextManaged):
    def __init__(
            self,
            *,
            chat_cfg: ChatConfig,
            parent_injector: inj.AsyncInjector | None = None,
    ) -> None:
        super().__init__()

        self._chat_cfg = chat_cfg
        self._parent_injector = parent_injector

        self._driver: DriverManager._Driver | None = None

    #

    class _Driver:
        def __init__(
                self,
                aes: contextlib.AsyncExitStack,
                injector: inj.AsyncInjector,
                cdi: ChatDriverInterface,
        ) -> None:
            super().__init__()

            self.aes = aes
            self.injector = injector
            self.cdi = cdi

    #

    _state: ta.Literal['new', 'entered', 'exited'] = 'new'

    async def __aenter__(self) -> ta.Self:
        check.state(self._state == 'new')
        self._state = 'entered'
        return self

    async def __aexit__(self, et, e, tb):
        if self._state != 'entered':
            return
        self._state = 'exited'

        if (driver := self._driver) is None:
            return

        self._driver = None

        await check.not_none(driver.aes).__aexit__(None, None, None)

    #

    async def get_chat_driver_interface(self) -> ChatDriverInterface:
        check.state(self._state == 'entered')

        if (driver := self._driver) is not None:
            return driver.cdi

        aes = contextlib.AsyncExitStack()
        await aes.__aenter__()

        ec = inj.collect_elements(inj.as_elements(
            inj.bind(contextlib.AsyncExitStack, to_const=aes),

            bind_driver_internal(self._chat_cfg),
        ))

        injector = await inj.create_async_injector(ec, parent=self._parent_injector)

        cdi = await injector[ChatDriverInterface]

        self._driver = self._Driver(
            aes,
            injector,
            cdi,
        )

        return cdi
