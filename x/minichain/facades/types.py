import typing as ta
import uuid

from omlish import lang


##


class Facade(lang.Abstract):
    def handle_user_input(
            self,
            text: str,
            *,
            input_uuid: uuid.UUID | None = None,
    ) -> ta.Awaitable[None]:
        raise NotImplementedError
