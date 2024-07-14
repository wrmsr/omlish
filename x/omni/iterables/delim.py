import functools
import io
import typing as ta


def yield_delimited_str_chunks(
        src: ta.Union[ta.IO, ta.Callable[[], str]],
        delimiter: str,
        *,
        chunk_size: int = 0xFFFF,
) -> ta.Generator[ta.Generator[str, None, None], None, None]:
    chunk_size = max(len(delimiter) + 1, chunk_size)
    if isinstance(src, (ta.TextIO, io.TextIOBase)):
        src = functools.partial(src.read, chunk_size)
    if not callable(src):
        raise TypeError(src)

    chunk = None
    last_chunk = None

    def inner():
        nonlocal chunk
        nonlocal last_chunk

        while True:
            if not chunk:
                chunk = src()
                if not isinstance(chunk, str):
                    raise TypeError(chunk)
                if not chunk:
                    chunk = None
                    if last_chunk:
                        if delimiter in last_chunk:  # type: ignore
                            out, _, chunk = last_chunk.partition(delimiter)
                            yield out
                        else:
                            yield last_chunk
                        last_chunk = None
                    break

            combined = (last_chunk or '') + chunk
            if delimiter in combined:
                out, _, chunk = combined.partition(delimiter)
                yield out
                last_chunk = None
                break

            if last_chunk:
                yield last_chunk
            last_chunk = chunk
            chunk = None

    while True:
        yield inner()
        if chunk is None:
            break
