# @omlish-lite


##


class BuffersError(Exception):
    pass


class NeedMoreData(BuffersError):  # noqa
    """
    Raised when an operation cannot complete because insufficient bytes are currently buffered.

    This is intentionally distinct from EOF: it means "try again after feeding more bytes".
    """


class BufferLimitError(ValueError, BuffersError):  # noqa
    """
    Base class for buffer/framing limit violations.

    Subclasses inherit from ValueError so existing tests expecting ValueError continue to pass.
    """


class BufferTooLarge(BufferLimitError):  # noqa
    """
    Buffered data exceeded a configured cap without finding a boundary that would allow progress.

    Typically indicates an unframed stream, a missing delimiter, or an upstream not enforcing limits.
    """


class FrameTooLarge(BufferLimitError):  # noqa
    """
    A single decoded frame (payload before its boundary delimiter/length) exceeded a configured max size.
    """


class BufferStateError(RuntimeError, BuffersError):  # noqa
    """
    Base class for invalid buffer state transitions (e.g., coalescing while a reservation is outstanding).

    Subclasses inherit from RuntimeError so existing tests expecting RuntimeError continue to pass.
    """


class OutstandingReserve(BufferStateError):  # noqa
    """A reserve() is outstanding; an operation requiring stable storage cannot proceed."""


class NoOutstandingReserve(BufferStateError):  # noqa
    """commit() was called without a preceding reserve()."""
