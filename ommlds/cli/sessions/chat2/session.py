import dataclasses as dc

from ..base import Session
from .configs import ChatSessionConfig


##


class Chat2Session(Session['Chat2Session.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config, ChatSessionConfig):
        pass

    def __init__(
            self,
            config: Config,
    ) -> None:
        super().__init__(config)

    async def run(self) -> None:
        # if self._config.new:
        #     state = self._state_manager.clear_state()
        # else:
        #     state = self._state_manager.get_state()

        raise NotImplementedError
