import abc
import typing as ta

from omlish import check
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


##


class BaseTokenizer(Tokenizer, lang.Abstract):
    def __init__(
            self,
            vocab: Vocab,
            specials: SpecialTokens,
    ) -> None:
        super().__init__()

        self._vocab = check.isinstance(vocab, Vocab)
        self._specials = check.isinstance(specials, SpecialTokens)

    @property
    def vocab(self) -> Vocab:
        return self._vocab

    @property
    def specials(self) -> SpecialTokens:
        return self._specials

    #

    def encode(
            self,
            text: str,
    ) -> list[Token]:
        return self._encode(
            text,
        )

    @abc.abstractmethod
    def _encode(
            self,
            text: str,
    ) -> list[Token]:
        raise NotImplementedError

    #

    def decode(
            self,
            tokens: ta.Iterable[Token],
    ) -> str:
        return self._decode(
            tokens,
        )

    @abc.abstractmethod
    def _decode(
            self,
            tokens: ta.Iterable[Token],
    ) -> str:
        raise NotImplementedError
