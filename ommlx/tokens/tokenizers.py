import abc
import typing as ta

from omlish import lang

from .specials import SpecialTokens
from .types import Token
from .vocabs import Vocab


##


class Tokenizer(lang.Abstract):
    @property
    @abc.abstractmethod
    def vocab(self) -> Vocab:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def specials(self) -> SpecialTokens:
        raise NotImplementedError

    @abc.abstractmethod
    def encode(
            self,
            text: str,
    ) -> list[Token]:
        raise NotImplementedError

    @abc.abstractmethod
    def decode(
            self,
            tokens: ta.Iterable[Token],
    ) -> str:
        raise NotImplementedError
