import itertools
import typing as ta

from omlish import check

from ..types import Tokenizer
from .base import BaseStreamingDetokenizer


##


class BpeStreamingDetokenizer(BaseStreamingDetokenizer):
    """
    A streaming detokenizer for OpenAI style BPE models.

    It adds tokens to the text if the next token starts with a space similar to the SPM detokenizer.
    """

    _space_matches = ('.', '?', '!', ',', "n't", "'m", "'s", "'ve", "'re")

    def __init__(
            self,
            tokenizer: Tokenizer,
    ) -> None:
        super().__init__()

        self._clean_spaces = tokenizer.clean_up_tokenization_spaces

        # Extract the tokens in a list from id to text
        self._token_map: list[str | None] = [None] * len(tokenizer.vocab)
        for value, token in tokenizer.vocab.items():
            self._token_map[token] = value

        self._unflushed = ''

        # Make the BPE byte decoder from https://github.com/openai/gpt-2/blob/master/src/encoder.py
        self._make_byte_decoder()

    def reset(self) -> None:
        super().reset()

        self._unflushed = ''

    def _decode_bytes(self, seq: str) -> str:
        ba = bytearray()
        for c in seq:
            res = self._byte_decoder.get(c, False)
            if res:
                ba.append(res)
            else:
                ba.extend(bytes(c, 'utf-8'))
        return ba.decode('utf-8', 'replace')

    def _maybe_trim_space(self, current_text: str) -> str:
        if len(current_text) == 0:
            return current_text

        elif current_text[0] != ' ':
            return current_text

        elif not self._text:
            return current_text[1:]

        elif self._clean_spaces and current_text[1:].startswith(self._space_matches):
            return current_text[1:]

        return current_text

    def add_token(self, token: int) -> None:
        self._tokens.append(token)
        v = check.not_none(self._token_map[token])
        self._unflushed += v
        text = self._decode_bytes(self._unflushed)

        # For multi-byte utf-8 wait until they are complete. For single spaces wait until the next token to clean it if
        # needed.
        if (
                not text.endswith('\ufffd') and
                not (len(v) == 1 and self._byte_decoder[v[0]] == 32)
        ):
            self._text += self._maybe_trim_space(text)
            self._unflushed = ''

    def finalize(self) -> None:
        current_text = bytearray(
            self._byte_decoder[c]
            for c in self._unflushed
        ).decode('utf-8', 'replace')
        self._text += self._maybe_trim_space(current_text)

        self._unflushed = ''

    #

    _byte_decoder: ta.ClassVar[ta.Mapping[str, int]]

    @classmethod
    def _make_byte_decoder(cls) -> ta.Mapping[str, int]:
        """See https://github.com/openai/gpt-2/blob/master/src/encoder.py for the rationale."""

        try:
            return cls._byte_decoder
        except AttributeError:
            pass

        char_to_bytes: dict[str, int] = {}

        limits = [
            0,
            ord('!'),
            ord('~') + 1,
            ord('¡'),
            ord('¬') + 1,
            ord('®'),
            ord('ÿ') + 1,
        ]

        n = 0
        for i, (start, stop) in enumerate(itertools.pairwise(limits)):
            if i % 2 == 0:
                for b in range(start, stop):
                    char_to_bytes[chr(2**8 + n)] = b
                    n += 1
            else:
                for b in range(start, stop):
                    char_to_bytes[chr(b)] = b

        cls._byte_decoder = char_to_bytes
        return char_to_bytes
