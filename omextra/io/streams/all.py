from .adapters import (  # noqa
    ByteStreamBufferReaderAdapter,
    ByteStreamBufferWriterAdapter,
    BytesIoByteStreamBuffer,
)

from .errors import (  # noqa
    ByteStreamBufferError,

    NeedMoreDataByteStreamBufferError,

    LimitByteStreamBufferError,
    BufferTooLargeByteStreamBufferError,
    FrameTooLargeByteStreamBufferError,

    StateByteStreamBufferError,
    OutstandingReserveByteStreamBufferError,
    NoOutstandingReserveByteStreamBufferError,
)

from .framing import (  # noqa
    LongestMatchDelimiterByteStreamFramer,
)

from .linear import (  # noqa
    LinearByteStreamBuffer,
)

from .reading import (  # noqa
    ByteStreamBufferReader,
)

from .scanning import (  # noqa
    ScanningByteStreamBuffer,
)

from .segmented import (  # noqa
    SegmentedByteStreamBufferView,
    SegmentedByteStreamBuffer,
)

from .types import (  # noqa
    BytesLike,

    ByteStreamBufferView,
    ByteStreamBuffer,
    MutableByteStreamBuffer,
)

from .utils import (  # noqa
    ByteStreamBuffers,
)


##


NeedMoreData = NeedMoreDataByteStreamBufferError

BufferTooLarge = BufferTooLargeByteStreamBufferError
FrameTooLarge = FrameTooLargeByteStreamBufferError

OutstandingReserve = OutstandingReserveByteStreamBufferError
NoOutstandingReserve = NoOutstandingReserveByteStreamBufferError

#

can_bytes = ByteStreamBuffers.can_bytes
iter_bytes_segments = ByteStreamBuffers.iter_bytes_segments
to_bytes = ByteStreamBuffers.to_bytes
bytes_len = ByteStreamBuffers.bytes_len
