import typing as ta

import transformers as tfm

from omlish import check
from omlish import collections as col

from ..specials import SpecialToken
from ..specials import SpecialTokens
from ..specials import StandardSpecialTokens
from ..types import Token
from ..types import TokenStr
from ..vocabs import Vocab
from .base import BaseTokenizer


##


def build_vocab(tfm_tokenizer: tfm.PreTrainedTokenizerBase) -> Vocab:
    return Vocab([
        (ta.cast(Token, i), TokenStr(s))
        for s, i in tfm_tokenizer.get_vocab().items()
    ])


#


SPECIAL_TOKEN_ATTR_MAP: col.BiMap[type[SpecialToken], str] = col.make_bi_map({
    StandardSpecialTokens.Bos: 'bos_token_id',
    StandardSpecialTokens.Eos: 'eos_token_id',
    StandardSpecialTokens.Unk: 'unk_token_id',
    StandardSpecialTokens.Sep: 'sep_token_id',
    StandardSpecialTokens.Pad: 'pad_token_id',
    StandardSpecialTokens.Cls: 'cls_token_id',
    StandardSpecialTokens.Mask: 'mask_token_id',
})


def build_specials(tfm_tokenizer: tfm.PreTrainedTokenizerBase) -> SpecialTokens:
    return SpecialTokens.from_dict({
        st: getattr(tfm_tokenizer, a)
        for st, a in SPECIAL_TOKEN_ATTR_MAP.items()
    })


##


class TransformersTokenizer(BaseTokenizer):
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
    ) -> list[Token]:
        ts = self._tfm_tokenizer.tokenize(text)
        ids = self._tfm_tokenizer.convert_tokens_to_ids(ts)
        return ids

    def _decode(
            self,
            tokens: ta.Iterable[Token],
    ) -> str:
        return self._tfm_tokenizer.decode(tokens)


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
