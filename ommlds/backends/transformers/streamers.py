import functools
import typing as ta

import transformers as tfm


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


class CancellableTextStreamer(tfm.TextStreamer):
    class Callback(ta.Protocol):
        def __call__(self, text: str, *, stream_end: bool) -> None: ...

    def __init__(
            self,
            tokenizer: tfm.AutoTokenizer,
            callback: Callback,
            *,
            skip_prompt: bool = False,
            **decode_kwargs: ta.Any,
    ) -> None:
        super().__init__(
            tokenizer,
            skip_prompt=skip_prompt,
            **decode_kwargs,
        )

        self.callback = callback

    _cancelled: bool = False

    #

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def cancel(self) -> None:
        self._cancelled = True

    class Cancelled(BaseException):  # noqa
        pass

    @staticmethod
    def ignoring_cancelled(fn: ta.Callable[P, T]) -> ta.Callable[P, T | None]:
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except CancellableTextStreamer.Cancelled:
                pass

        return inner

    def _maybe_raise_cancelled(self) -> None:
        if self._cancelled:
            raise CancellableTextStreamer.Cancelled

    #

    def put(self, value: ta.Any) -> None:
        self._maybe_raise_cancelled()
        super().put(value)
        self._maybe_raise_cancelled()

    def on_finalized_text(self, text: str, stream_end: bool = False) -> None:
        self._maybe_raise_cancelled()
        self.callback(text, stream_end=stream_end)
        self._maybe_raise_cancelled()
