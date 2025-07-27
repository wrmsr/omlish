from ..types import Tokenizer
from .base import BaseStreamingDetokenizer


##


class NaiveStreamingDetokenizer(BaseStreamingDetokenizer):
    """
    NaiveStreamingDetokenizer relies on the underlying tokenizer implementation and should work with every tokenizer.

    Its complexity is O(T^2) where T is the longest line since it will repeatedly detokenize the same tokens until a new
    line is generated.
    """

    def __init__(
            self,
            tokenizer: Tokenizer,
    ) -> None:
        super().__init__()

        self._tokenizer = tokenizer
        self._tokenizer.decode([0])

        self._current_tokens: list[int] = []
        self._current_text = ''

    def reset(self) -> None:
        super().reset()

        self._current_tokens = []
        self._current_text = ''

    def add_token(self, token: int) -> None:
        self._current_tokens.append(token)
        self._tokens.append(token)

    def finalize(self) -> None:
        self._text += self._tokenizer.decode(self._current_tokens)
        self._current_tokens = []
        self._current_text = ''

    @property
    def text(self) -> str:
        if self._current_tokens:
            self._current_text = self._tokenizer.decode(self._current_tokens)
            if self._current_text.endswith('\ufffd') or (
                    self._tokenizer.clean_up_tokenization_spaces and
                    self._current_text and
                    self._current_text[-1] == ' '
            ):
                self._current_text = self._current_text[:-1]

        if self._current_text and self._current_text[-1] == '\n':
            self._text += self._current_text
            self._current_tokens.clear()
            self._current_text = ''

        return self._text + self._current_text
