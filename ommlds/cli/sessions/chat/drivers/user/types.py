import abc
import typing as ta

from omlish import lang

from ...... import minichain as mc


##


class UserChatInput(lang.Abstract):
    @abc.abstractmethod
    def get_next_user_messages(self) -> ta.Awaitable['mc.UserChat']:
        raise NotImplementedError
