# Overview

IO utilities including compression, coroutine/sans-io helpers, file descriptor IO, and custom IO implementations.
Emphasizes incremental operation and framework-agnostic IO handling.

# Key Components

- **[compress](https://github.com/wrmsr/omlish/blob/master/omlish/io/compress)** - Compression utilities with
  incremental operation:
  - Abstraction over various compression schemes (gzip, bzip2, lz4, zstd, snappy, brotli).
  - Incremental/streaming compression and decompression.
  - **[gzip](https://github.com/wrmsr/omlish/blob/master/omlish/io/compress/gzip.py)** - Incremental reformulation of
    stdlib gzip.
- **[coro](https://github.com/wrmsr/omlish/blob/master/omlish/io/coro)** - Coroutine/sans-io utilities:
  - IO operations as coroutines for framework-agnostic code.
  - Works in sync, async, or any event loop context.
- **[fdio](https://github.com/wrmsr/omlish/blob/master/omlish/io/fdio)** - File descriptor IO dispatch:
  - Classic selector-style IO dispatch implementation.
  - Alternative to asyncio for contexts where threading is unsuitable (process supervisors, forking code).
  - Akin to deprecated `asyncore` but modernized.
- **[generators](https://github.com/wrmsr/omlish/blob/master/omlish/io/generators)** - Generator-based IO utilities.
- **abc** - Abstract base classes for IO operations.
- **buffers** - Buffer implementations for IO operations.
- **fileno** - File descriptor utilities.
- **pyio** - Pure Python IO implementations.
- **readers** - Reader abstractions and implementations.

# Key Features

- **Incremental compression** - Stream compression without loading entire files into memory.
- **Sans-io style** - Separate protocol logic from IO for framework independence.
- **Selector-based dispatch** - Event loop suitable for process supervisors and fork-safe code.
- **Compression abstraction** - Unified interface over multiple compression backends.
- **Custom IO** - Build custom IO streams with standard Python IO interfaces.

# Notable Modules

- **[compress/abc](https://github.com/wrmsr/omlish/blob/master/omlish/io/compress/abc.py)** - Compression interface
  abstractions.
- **[compress/gzip](https://github.com/wrmsr/omlish/blob/master/omlish/io/compress/gzip.py)** - Incremental gzip
  implementation.
- **[fdio](https://github.com/wrmsr/omlish/blob/master/omlish/io/fdio)** - Selector-style IO dispatch for file
  descriptors.
- **[coro](https://github.com/wrmsr/omlish/blob/master/omlish/io/coro)** - Coroutine-style IO utilities.
- **[buffers](https://github.com/wrmsr/omlish/blob/master/omlish/io/buffers.py)** - Buffer implementations.
- **[readers](https://github.com/wrmsr/omlish/blob/master/omlish/io/readers.py)** - Reader utilities.

# Example Usage

```python
from omlish.io import compress

# Incremental gzip compression
with compress.open_compressed('file.gz', 'wb', 'gzip') as f:
    for chunk in large_data:
        f.write(chunk)  # Compressed incrementally

# Detect and decompress any format
with compress.open_compressed('file.??', 'rb', 'auto') as f:
    data = f.read()  # Auto-detects compression format
```

# Design Philosophy

IO utilities should:
- **Support incremental operation** - Don't require loading entire files into memory.
- **Be framework-agnostic** - Work with sync, async, or custom event loops.
- **Abstract backend differences** - Unified API over different compression libraries, etc.
- **Be suitable for production** - Handle edge cases, resource management, error conditions.

The `fdio` package is particularly notable as it provides an event loop suitable for:
- Process supervisors that need to fork (asyncio uses threads, making forking unsafe)
- Code that can't use asyncio/trio/anyio
- Classic selector-style programming without modern async frameworks

See `omlish.http.coro` for HTTP server code using this style, and `ominfra.supervisor` for a process supervisor built
on fdio.
