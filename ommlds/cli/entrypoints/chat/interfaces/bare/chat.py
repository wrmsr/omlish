from ...... import minichain as mc


##


class BareUserInputSender(mc.facades.UserInputSender):
    def __init__(
            self,
            *,
            facade: mc.facades.Facade,
    ) -> None:
        super().__init__()

        self._facade = facade

    async def send_user_input(self, text: str, *, no_echo: bool = False) -> None:
        if not no_echo:
            print('> ' + text)

        print()
        print('<')
        print()

        await self._facade.handle_user_input(text)

        print()
