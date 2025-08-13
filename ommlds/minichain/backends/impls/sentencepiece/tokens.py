import typing as ta

import sentencepiece as spm

from omlish import check

from .... import tokens as tks


##


def build_vocab(spm_tokenizer: spm.SentencePieceProcessor) -> tks.Vocab:
    return tks.Vocab([
        (ta.cast(tks.Token, i), tks.TokenStr(spm_tokenizer.id_to_piece(i)))  # noqa
        for i in range(spm_tokenizer.get_piece_size())  # noqa
    ])


def build_specials(spm_tokenizer: spm.SentencePieceProcessor) -> tks.SpecialTokens:
    # FIXME
    return tks.SpecialTokens([])


##


class SentencepieceTokenizer(tks.BaseTokenizer):
    def __init__(
            self,
            spm_tokenizer: spm.SentencePieceProcessor,
    ) -> None:
        self._spm_tokenizer = check.isinstance(spm_tokenizer, spm.SentencePieceProcessor)

        super().__init__(
            build_vocab(spm_tokenizer),
            build_specials(spm_tokenizer),
        )

    @property
    def spm_tokenizer(self) -> spm.SentencePieceProcessor:
        return self._spm_tokenizer

    #

    def _encode(
            self,
            text: str,
    ) -> list[tks.Token]:
        return self._spm_tokenizer.encode(text)

    def _decode(
            self,
            tokens: ta.Iterable[tks.Token],
    ) -> str:
        return self._spm_tokenizer.decode(tokens)


##


def _main() -> None:
    spm_tokenizer = spm.SentencePieceProcessor(model_file='tokenizer.model')
    tkz = SentencepieceTokenizer(spm_tokenizer)

    text = 'Using a Transformer network is simple'
    tokens = tkz.encode(text)
    print(tokens)
    text2 = tkz.decode(tokens)
    print(text2)


if __name__ == '__main__':
    _main()
