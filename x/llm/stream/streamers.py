import typing as ta

import transformers as tfm


##


class CancellableTextStreamer(tfm.TextStreamer):
    class Callback(ta.Protocol):
        def __call__(self, text: str, *, stream_end: bool) -> None: ...

    class Cancelled(BaseException):  # noqa
        pass

    def __init__(
            self,
            callback: Callback,
            tokenizer: tfm.AutoTokenizer,
            *,
            skip_prompt: bool = False,
            **decode_kwargs: ta.Any
    ) -> None:
        super().__init__(
            tokenizer,
            skip_prompt=skip_prompt,
            **decode_kwargs,
        )

        self._cancelled = False
        self.callback = callback

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def cancel(self) -> None:
        self._cancelled = True

    def _maybe_raise_cancelled(self) -> None:
        if self._cancelled:
            raise CancellableTextStreamer.Cancelled

    def put(self, value: ta.Any) -> None:
        self._maybe_raise_cancelled()
        super().put(value)
        self._maybe_raise_cancelled()

    def on_finalized_text(self, text: str, stream_end: bool = False) -> None:
        self._maybe_raise_cancelled()
        self.callback(text, stream_end=stream_end)
        self._maybe_raise_cancelled()
