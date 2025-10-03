import typing as ta

import transformers as tfm

from omlish import check
from omlish import collections as col

from .... import tokens as tks


##


def build_vocab(tfm_tokenizer: tfm.PreTrainedTokenizerBase) -> tks.Vocab:
    return tks.Vocab([
        (ta.cast(tks.Token, i), tks.TokenStr(s))
        for s, i in tfm_tokenizer.get_vocab().items()
    ])


#


SPECIAL_TOKEN_ATTR_MAP: col.BiMap[type[tks.SpecialToken], str] = col.make_bi_map({
    tks.Bos: 'bos_token_id',
    tks.Eos: 'eos_token_id',
    tks.Unk: 'unk_token_id',
    tks.Sep: 'sep_token_id',
    tks.Pad: 'pad_token_id',
    tks.Cls: 'cls_token_id',
    tks.Mask: 'mask_token_id',
})


def build_specials(tfm_tokenizer: tfm.PreTrainedTokenizerBase) -> tks.SpecialTokens:
    return tks.SpecialTokens.from_dict({
        st: getattr(tfm_tokenizer, a)
        for st, a in SPECIAL_TOKEN_ATTR_MAP.items()
    })


##


class TransformersTokenizer(tks.BaseTokenizer):
    def __init__(
            self,
            tfm_tokenizer: tfm.PreTrainedTokenizerBase,
    ) -> None:
        self._tfm_tokenizer = check.isinstance(tfm_tokenizer, tfm.PreTrainedTokenizerBase)

        super().__init__(
            build_vocab(tfm_tokenizer),
            build_specials(tfm_tokenizer),
        )

    @property
    def tfm_tokenizer(self) -> tfm.PreTrainedTokenizerBase:
        return self._tfm_tokenizer

    #

    def _encode(
            self,
            text: str,
    ) -> list[tks.Token]:
        ts = self._tfm_tokenizer.tokenize(text)
        ids = self._tfm_tokenizer.convert_tokens_to_ids(ts)
        return ids

    def _decode(
            self,
            tokens: ta.Iterable[tks.Token],
    ) -> str:
        return self._tfm_tokenizer.decode(tokens)  # type: ignore[arg-type]


##


def _main() -> None:
    tfm_tokenizer = tfm.AutoTokenizer.from_pretrained('bert-base-cased')
    tkz = TransformersTokenizer(tfm_tokenizer)

    text = 'Using a Transformer network is simple'
    tokens = tkz.encode(text)
    print(tokens)
    text2 = tkz.decode(tokens)
    print(text2)


if __name__ == '__main__':
    _main()
