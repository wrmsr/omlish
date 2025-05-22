import typing as ta

import transformers as tfm

from omlish import check

from .detokenization.base import StreamingDetokenizer
from .types import Tokenizer


##


class Tokenization:
    def __init__(
            self,
            tokenizer: Tokenizer,
            detokenizer: StreamingDetokenizer,
            *,
            eos_token_ids: ta.Iterable[int] | None = None,
    ) -> None:
        super().__init__()

        self._tokenizer = check.isinstance(tokenizer, tfm.PreTrainedTokenizerBase)
        self._detokenizer = check.isinstance(detokenizer, StreamingDetokenizer)

        if eos_token_ids is None:
            eos_token_ids = {tokenizer.eos_token_id}
        self._eos_token_ids = set(eos_token_ids)

    @property
    def tokenizer(self) -> Tokenizer:
        return self._tokenizer

    @property
    def detokenizer(self) -> StreamingDetokenizer:
        return self._detokenizer

    @property
    def eos_token_ids(self) -> ta.AbstractSet[int]:
        return self._eos_token_ids

    def add_eos_token(self, token: int | str) -> None:
        try:
            token_id = int(token)
        except ValueError:
            token_id = self._tokenizer.convert_tokens_to_ids(token)

        if token_id is None:
            raise ValueError(f"'{token}' is not a token for this tokenizer")

        self._eos_token_ids.add(token_id)
