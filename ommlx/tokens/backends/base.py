import abc
import typing as ta

from omlish import check

from ..specials import SpecialTokens
from ..tokenizers import Tokenizer
from ..types import Token
from ..vocabs import Vocab


##


class BaseTokenizer(Tokenizer, abc.ABC):
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
