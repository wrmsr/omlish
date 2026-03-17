# ByteStream Buffers

A **Netty/Tokio-inspired byte buffer system** for building protocol parsers and network servers in pure Python.

## Overview

This package provides:
- **Zero-copy segmented buffers** for efficient protocol parsing
- **Stream-correct search** across segment boundaries
- **Framing codecs** (delimiter-based, length-prefixed)
- **Binary read helpers** for protocol decoding
- **File-like adapters** for interop with existing code

## Quick Start

### Basic Usage

```python
from omlish.io.streams.segmented import SegmentedByteStreamBuffer

# Create a buffer and write some data
buf = SegmentedByteStreamBuffer(chunk_size=4096)
buf.write(b'Hello, World!\r\n')

# Search for delimiter
pos = buf.find(b'\r\n')  # Returns 13

# Split off a frame
frame = buf.split_to(pos)
buf.advance(2)  # Skip the delimiter

print(frame.tobytes())  # b'Hello, World!'
```

### Delimiter-Based Framing

```python
from omlish.io.streams.framing import LongestMatchDelimiterByteStreamFrameDecoder
from omlish.io.streams.segmented import SegmentedByteStreamBuffer

buf = SegmentedByteStreamBuffer(chunk_size=4096)
framer = LongestMatchDelimiterByteStreamFrameDecoder(
    delims=[b'\r\n', b'\n'],  # Handles overlapping delimiters correctly
    keep_ends=False,
)

# Feed data
buf.write(b'Line 1\r\nLine 2\nLine 3\r\n')

# Decode frames
frames = framer.decode(buf)
for frame in frames:
    print(frame.tobytes())
# Output:
# b'Line 1'
# b'Line 2'
# b'Line 3'
```

### Length-Prefixed Framing

```python
from omlish.io.streams.framing import LengthFieldByteStreamFrameDecoder
from omlish.io.streams.linear import LinearByteStreamBuffer

buf = LinearByteStreamBuffer()
framer = LengthFieldByteStreamFrameDecoder(
    length_field_offset=0,
    length_field_length=4,
    initial_bytes_to_strip=4,
    byteorder='big',
)

# Feed a length-prefixed message: [length: 4 bytes][payload: N bytes]
buf.write(b'\x00\x00\x00\x05Hello')  # 5-byte payload

frames = framer.decode(buf)
print(frames[0].tobytes())  # b'Hello'
```

### Binary Protocol Parsing

```python
from omlish.io.streams.linear import LinearByteStreamBuffer
from omlish.io.streams.reading import ByteStreamBufferReader

buf = LinearByteStreamBuffer()
reader = ByteStreamBufferReader(buf)

# Feed binary data
buf.write(b'\x01\x00\x0a\x00\x00\x00\x64')

# Parse structured data
version = reader.read_u8()        # 1
flags = reader.read_u16_be()      # 10
timestamp = reader.read_u32_be()  # 100
```

### Reserve/Commit for Zero-Copy Reads

```python
import socket

from omlish.io.streams.segmented import SegmentedByteStreamBuffer

buf = SegmentedByteStreamBuffer(chunk_size=8192)
sock = socket.socket()

# Reserve space and read directly into buffer
mv = buf.reserve(4096)
n = sock.recv_into(mv)
buf.commit(n)  # Make the received bytes readable
```

## Buffer Implementations

Choose the right backend for your use case:

| Buffer | Best For | Tradeoffs |
|--------|----------|-----------|
| `DirectByteStreamBuffer` | Parsing existing bytes (read-only) | Zero-copy, but immutable |
| `SegmentedByteStreamBuffer` | Network I/O, streaming protocols | Complex internals, zero-copy `split_to` |
| `LinearByteStreamBuffer` | Fast header parsing, small buffers | `split_to` copies, needs compaction |
| `BytesIoByteStreamBuffer` | BytesIO interop | Can pin memory, not recommended |

### Optimization: ScanningByteStreamBuffer

Wrap any buffer to cache negative search results for trickle-data scenarios:

```python
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer

inner = SegmentedByteStreamBuffer(chunk_size=4096)
buf = ScanningByteStreamBuffer(inner)

# Repeated searches on trickle data are optimized
buf.write(b'partial')
buf.find(b'\r\n')  # -1, caches scan position

buf.write(b' data')
buf.find(b'\r\n')  # -1, only scans new bytes

buf.write(b'\r\n')
buf.find(b'\r\n')  # Found!
```

## Key Concepts

### Views vs Copies

- **`peek()` / `segments()`** - Zero-copy views (ephemeral, invalidated by mutations)
- **`split_to(n)`** - Stable views (remain valid forever)
- **`tobytes()`** - Explicit copy to contiguous `bytes`

### Stream-Correct Search

`find()` and `rfind()` work correctly even when the pattern spans segment boundaries:

```python
from omlish.io.streams.segmented import SegmentedByteStreamBuffer

buf = SegmentedByteStreamBuffer(chunk_size=4)
buf.write(b'ab')
buf.write(b'cd')
# Internally: [b'ab', b'cd']

pos = buf.find(b'bc')  # Returns 1 (correctly finds cross-segment match)
```

### Reserve/Commit Model

- Only one reservation at a time
- Reserved space is not readable until committed
- Enables zero-copy reads from sockets (`recv_into`)

## File-Like Adapters

Bridge buffers to/from file-like objects:

```python
from omlish.io.streams.adapters import ByteStreamBufferBytesReaderAdapter
from omlish.io.streams.linear import LinearByteStreamBuffer

buf = LinearByteStreamBuffer()
buf.write(b'Hello, World!')

# Wrap as file-like reader
reader = ByteStreamBufferBytesReaderAdapter(buf, policy='return_partial')
data = reader.read(5)  # b'Hello'
```

## Error Handling

```python
from omlish.io.streams.errors import (
    NeedMoreDataByteStreamBufferError,      # Insufficient bytes buffered
    BufferTooLargeByteStreamBufferError,    # Buffer exceeded max_size
    FrameTooLargeByteStreamBufferError,     # Frame exceeded max_size
    OutstandingReserveByteStreamBufferError,  # Invalid state (reserve active)
)
```

## Design Philosophy

- **Explicit over implicit** - Copy boundaries are clear (`tobytes()` vs `peek()`)
- **Composable** - Small, focused components that chain together
- **Bounded growth** - Everything has optional `max_size` limits
- **Pure Python** - No dependencies, works in any runtime (sync/async/threaded)
- **Correct first** - Resilience and clarity over maximum performance

See [DESIGN.md](DESIGN.md) for architectural deep-dive and rationale.

## Common Patterns

### HTTP Request Parsing

```python
buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(chunk_size=8192))
framer = LongestMatchDelimiterByteStreamFrameDecoder(
    delims=[b'\r\n'],
    max_size=8192,
)

# Feed data from socket
buf.write(received_data)

# Parse request line
lines = framer.decode(buf)
if lines:
    request_line = lines[0].tobytes().decode('ascii')
```

### Custom Binary Protocol

```python
reader = ByteStreamBufferReader(buf)

# Read header
magic = reader.read_u32_be()
if magic != 0xDEADBEEF:
    raise ValueError('Invalid magic')

msg_type = reader.read_u8()
length = reader.read_u16_be()

# Read payload
payload = reader.read_bytes(length)
```

### Streaming with Backpressure

```python
buf = SegmentedByteStreamBuffer(max_size=1024 * 1024)  # 1MB limit

try:
    buf.write(incoming_data)
except BufferTooLargeByteStreamBufferError:
    # Signal backpressure to upstream
    pause_reading()
```

## License

See repository root for license information.
