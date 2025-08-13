import typing as ta

import tokenizers as tos

from omlish import check

from .... import tokens as tks


##


def build_vocab(tos_tokenizer: tos.Tokenizer) -> tks.Vocab:
    return tks.Vocab([
        (ta.cast(tks.Token, i), tks.TokenStr(s))
        for s, i in tos_tokenizer.get_vocab().items()
    ])


def build_specials(tos_tokenizer: tos.Tokenizer) -> tks.SpecialTokens:
    # FIXME
    return tks.SpecialTokens([])


##


class TokenizersTokenizer(tks.BaseTokenizer):
    def __init__(
            self,
            tos_tokenizer: tos.Tokenizer,
    ) -> None:
        self._tos_tokenizer = check.isinstance(tos_tokenizer, tos.Tokenizer)

        super().__init__(
            build_vocab(tos_tokenizer),
            build_specials(tos_tokenizer),
        )

    @property
    def tos_tokenizer(self) -> tos.Tokenizer:
        return self._tos_tokenizer

    #

    def _encode(
            self,
            text: str,
    ) -> list[tks.Token]:
        enc = self._tos_tokenizer.encode(text)
        return enc.ids

    def _decode(
            self,
            tokens: ta.Iterable[tks.Token],
    ) -> str:
        return self._tos_tokenizer.decode(tokens)


##


def _main() -> None:
    tos_tokenizer = tos.Tokenizer.from_pretrained('bert-base-uncased')
    tkz = TokenizersTokenizer(tos_tokenizer)

    text = 'Using a Transformer network is simple'
    tokens = tkz.encode(text)
    print(tokens)
    text2 = tkz.decode(tokens)
    print(text2)


if __name__ == '__main__':
    _main()
