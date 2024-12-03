import typing as ta

from omlish.io.compress._abc import NeedsInputDecompressor  # noqa
from omlish.io.compress.types import IncrementalDecompressor


class DecompressorIncrementalAdapter:
    """Adapts the decompressor API to a IncrementalDecompressor"""

    def __init__(
            self,
            factory: ta.Callable[..., NeedsInputDecompressor],
            *,
            trailing_error: tuple[BaseException, ...] = (),
    ) -> None:
        super().__init__()

        self._factory = factory
        self._trailing_error = trailing_error

    def __call__(self) -> IncrementalDecompressor:
        pos = 0

        data = None  # Default if EOF is encountered

        decompressor = self._factory()

        while True:
            # Depending on the input data, our call to the decompressor may not return any data. In this case, try again
            # after reading another block.
            while True:
                if decompressor.eof:
                    rawblock = decompressor.unused_data
                    if not rawblock:
                        rawblock = yield None
                    if not rawblock:
                        break

                    # Continue to next stream.
                    decompressor = self._factory()

                    try:
                        data = decompressor.decompress(rawblock)
                    except self._trailing_error:
                        # Trailing data isn't a valid compressed stream; ignore it.
                        break

                else:
                    if decompressor.needs_input:
                        rawblock = yield None
                        if not rawblock:
                            raise EOFError('Compressed file ended before the end-of-stream marker was reached')
                    else:
                        rawblock = b''

                    data = decompressor.decompress(rawblock)

                if data:
                    break

            if not data:
                yield b''
                return

            pos += len(data)
            yield data
