import abc
import typing as ta

from omlish import lang


##


class UserInputSenderGetter(lang.AsyncCachedFunc0['UserInputSender']):
    pass


class UserInputSender(lang.Abstract):
    @abc.abstractmethod
    def send_user_input(self, text: str, *, no_echo: bool = False) -> ta.Awaitable[None]:
        raise NotImplementedError
