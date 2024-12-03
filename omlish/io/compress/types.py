# ruff: noqa: UP007
import typing as ta


IncrementalCompressor: ta.TypeAlias = ta.Generator[
    ta.Union[
        bytes,  # Compressed output
        None,  # Need input
    ],
    ta.Union[
        bytes,  # Input bytes
        None,  # Need output
    ],
    None,
]


IncrementalDecompressor: ta.TypeAlias = ta.Generator[
    ta.Union[
        int,  # Need exactly n bytes
        None,  # Need any amount of bytes
        bytes,  # Uncompressed output
    ],
    ta.Union[
        bytes,  # Input bytes
        None,  # Need output
    ],
    None,
]
