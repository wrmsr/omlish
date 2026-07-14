import abc
import typing as ta

from omlish import lang


##


class StreamingDetokenizer(lang.Abstract):
    """
    The streaming detokenizer interface so that we can detokenize one token at a time.

    Example usage is as follows:

        detokenizer = ...

        # Reset the tokenizer state
        detokenizer.reset()

        for token in generate(...):
            detokenizer.add_token(token.item())

            # Contains the whole text so far. Some tokens may not be included
            # since it contains whole words usually.
            detokenizer.text

            # Contains the printable segment (usually a word) since the last
            # time it was accessed
            detokenizer.last_segment

            # Contains all the tokens added so far
            detokenizer.tokens

        # Make sure that we detokenize any remaining tokens
        detokenizer.finalize()

        # Now detokenizer.text should match tokenizer.decode(detokenizer.tokens)
    """

    @property
    @abc.abstractmethod
    def text(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def offset(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def tokens(self) -> ta.Sequence[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def add_token(self, token: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def finalize(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def last_segment(self) -> str:
        """Return the last segment of readable text since last time this property was accessed."""

        raise NotImplementedError


##


class BaseStreamingDetokenizer(StreamingDetokenizer, lang.Abstract):
    def __init__(self) -> None:
        super().__init__()

        self._text = ''
        self._offset = 0
        self._tokens: list[int] = []

    @property
    def text(self) -> str:
        return self._text

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def tokens(self) -> ta.Sequence[int]:
        return self._tokens

    def reset(self) -> None:
        self._text = ''
        self._offset = 0
        self._tokens = []

    def last_segment(self) -> str:
        text = self._text
        segment = text[self._offset:]
        self._offset = len(text)
        return segment
