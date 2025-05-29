from ..types import Tokenizer
from .base import BaseStreamingDetokenizer


##


class SpmStreamingDetokenizer(BaseStreamingDetokenizer):
    """
    A streaming detokenizer for SPM models.

    It adds tokens to the text if the next token starts with the special SPM underscore which results in linear
    complexity.
    """

    def __init__(
            self,
            tokenizer: Tokenizer,
            *,
            trim_space: bool = True,
    ) -> None:
        super().__init__()

        self._trim_space = trim_space
        self._sep = '\u2581'.encode()

        # Extract the tokens in a list from id to text
        self._token_map: list[bytes] = [b''] * (max(tokenizer.vocab.values()) + 1)
        for value, token in tokenizer.vocab.items():
            if value.startswith('<0x'):
                # Replace bytes with their value
                self._token_map[token] = bytes([int(value[3:5], 16)])
            else:
                self._token_map[token] = value.encode()

        self._unflushed = b''

    def reset(self) -> None:
        super().reset()

        self._unflushed = b''

    def _try_flush(self, *, force: bool = False) -> None:
        text = self._unflushed.replace(self._sep, b' ').decode('utf-8', 'replace')
        if not force and text.endswith('\ufffd'):
            return
        if not self._text and self._trim_space and text and text[0] == ' ':
            text = text[1:]
        self._text += text
        self._unflushed = b''

    def add_token(self, token: int) -> None:
        self._tokens.append(token)
        v = self._token_map[token]
        self._unflushed += v
        self._try_flush()

    def finalize(self) -> None:
        self._try_flush(force=True)
        self._unflushed = b''
