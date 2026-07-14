import typing as ta

import transformers as tfm


Tokenizer: ta.TypeAlias = tfm.PreTrainedTokenizerBase


##


class TokenizerProtocol(ta.Protocol):
    @property
    def vocab(self) -> ta.Mapping[str, int]: ...

    @property
    def eos_token_id(self) -> int: ...

    @property
    def bos_token(self) -> str | None: ...

    @property
    def clean_up_tokenization_spaces(self) -> bool: ...

    def decode(
            self,
            token_ids: int | list[int],
            # skip_special_tokens: bool = False,
            # clean_up_tokenization_spaces: bool | None = None,
            **kwargs: ta.Any,
    ) -> str:
        ...

    def convert_tokens_to_ids(
            self,
            tokens: str | list[str],
    ) -> int | list[int]:
        ...

    def encode(
            self,
            text: str | list[str] | list[int],
            *,
            # text_pair: ta.Union[str, list[str], list[int], None] = None,
            add_special_tokens: bool = True,
            # padding: ta.Union[
            #     bool,
            #     ta.Literal[
            #         'longest',
            #         'max_length',
            #         'do_not_pad',
            #     ],
            # ] = False,
            # truncation: ta.Union[
            #     bool,
            #     ta.Literal[
            #         'only_first',
            #         'only_second',
            #         'longest_first',
            #         'do_not_truncate',
            #     ],
            #     None,
            # ] = None,
            # max_length: int | None = None,
            # stride: int = 0,
            # padding_side: str | None = None,
            **kwargs: ta.Any,
    ) -> list[int]:
        ...
