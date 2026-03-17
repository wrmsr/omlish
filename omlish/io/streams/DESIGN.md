# Buffer System Design Notes — Historical Architecture Summary

This document captures the design rationale, constraints, and evolution of a **general-purpose byte buffer subsystem**
intended to support a **Netty-like, pipeline-oriented protocol toolkit in Python**. It is meant to serve as durable
architectural context for future development and onboarding, not as API documentation.

---

## 1. Problem Statement & Goals

The goal was to design a **foundational buffer layer** suitable for building protocol stacks in Python with the
following constraints:

- **Pure Python, no external dependencies**, compatible with Python 3.8+
- **Embeddable**: usable inside arbitrary runtimes (sync, async, fork-only, threaded, event-loop driven, or none at all)
- **Independent of asyncio / async-await**, but adaptable to them
- **Composable** and **pipeline-friendly**, favoring small chained transforms over large monolithic objects
- **Correctness and resilience first** (OOM avoidance, bounded growth, clear error signaling)
- **Low copy where possible**, but never at the expense of clarity or safety
- Explicitly **not performance-maximal**; Python-appropriate efficiency is sufficient

The buffer layer is treated as *infrastructure*: it must be robust enough that higher-level protocol code never needs to
second-guess its behavior.

---

## 2. Design Philosophy

### Composition over inheritance Rather than building large stateful readers/writers, the design favors:
- Small buffer objects with explicit operations (`find`, `split_to`, `coalesce`, etc.)
- Stateless helper functions layered atop buffers (binary reads, framing, decoding)
- Pipeline codecs that operate purely on buffers + views

### Explicit boundaries
- **Copy boundaries are explicit** (`tobytes`, `read_bytes`)
- **Mutation vs. presentation** is clearly distinguished
- **Ephemeral vs. stable views** are explicitly defined

### “Everything needs a timeout / limit” All operations that can grow memory unboundedly must be limitable:
- Per-buffer `max_size`
- Per-frame `max_size`
- Clear error types when limits are exceeded

---

## 3. Core Abstractions

### ByteStreamBuffer (conceptual) A readable byte container with:
- Logical length (`__len__`)
- Search (`find`, `rfind`) — *stream-correct*, across internal segmentation
- Non-consuming inspection (`peek`, `segments`)
- Consuming operations (`advance`, `split_to`)
- Contiguity guarantee (`coalesce(n)`)

Buffers are **not sequences** and are **not random-access containers** in the general sense:
- They may support indexed access incidentally
- But they are optimized for *prefix-oriented, streaming access*
- They are not intended for arbitrary slicing or mutation

---

## 4. Concrete Buffer Backends

### DirectByteStreamBuffer A read-only, zero-copy wrapper around existing bytes/bytearray/memoryview:

**Strengths**
- Zero-copy construction from existing data
- Always contiguous (trivial `coalesce`)
- Fast find/rfind delegating to optimized bytes methods
- Minimal overhead

**Use cases**
- Parsing fixed/immutable data (HTTP requests, protocol messages)
- Using framers/codecs on data already in memory
- Avoiding buffer allocation when mutation isn't needed

**Tradeoffs**
- Read-only (does not implement `MutableByteStreamBuffer`)

### SegmentedByteStreamBuffer A list-of-segments design (bytes / bytearray chunks):

**Strengths**
- Avoids pathological "large buffer pinned by tiny tail"
- Stable zero-copy views for `split_to`
- Natural fit for network chunking and streaming
- Optional chunking mode for small writes

**Tradeoffs**
- Search and coalescing require careful logic
- Segment count must be managed (coalescing / heuristics)

### LinearByteStreamBuffer A single `bytearray` + read/write indices:

**Strengths**
- Fast scanning and header parsing
- Naturally contiguous prefix
- Efficient `reserve` / `commit`

**Tradeoffs**
- `split_to` must copy to keep views stable
- Needs compaction heuristics to avoid growth from head advancement

### BytesIoByteStreamBuffer A `io.BytesIO`-backed implementation using `getbuffer()`:

**Strengths**
- Interoperability with existing BytesIO-based code
- Always contiguous

**Tradeoffs**
- Exported memoryviews can pin storage against resizing (BufferError)
- Not recommended as default backend (segmented/linear are more predictable)
- Primarily exists for interop scenarios

These backends intentionally cover different workload shapes; all conform to the same conceptual interface.

---

## 5. Views & Lifetime Rules

### ByteStreamBufferView / SegmentedByteStreamBufferView Objects returned from `split_to`:
- Represent bytes **removed** from the buffer
- Must remain **stable forever**
- May internally reference original segments or copies

### Ephemeral views Returned from:
- `peek`
- `segments`
- `coalesce`

Rules:
- Valid only until the next buffer mutation
- Never safe to hold across writes / advances
- Always exposed as `memoryview`

This mirrors real-world behavior in systems like Netty (retained slices) but without refcounting.

---

## 6. Coalescing Semantics (Key Design Point)

### `coalesce(n)` Guarantees the first `n` readable bytes are contiguous.

- **Non-consuming**
- May restructure internal storage
- Copies *only if necessary*, and only the minimal prefix
- Disallowed while a reservation is outstanding

Rationale:
- Python lacks efficient per-byte iteration
- Many operations (binary parsing, decoding) require contiguity
- Copying should happen *close to storage*, not in higher-level code

Unlike Netty or Tokio (where coalescing is implicit or pattern-based), this is an explicit primitive.

---

## 7. Reservation Model (`reserve` / `commit`)

Designed to support:
- Zero-copy reads from drivers
- Predictable memory behavior

Rules:
- Only one outstanding reservation at a time
- While reserved:
  - No reshaping operations allowed
  - No coalescing, splitting, advancing, or writing
- `commit(n)` appends exactly `n` bytes
- Reservation buffers are **temporary**, not views into live storage
  - Avoids Python `BufferError` pinning issues

This design was informed directly by pitfalls discovered when using `BytesIO.getbuffer()`.

---

## 8. Limits & Error Taxonomy

### Core error types
- `NeedMoreData`: insufficient bytes, retry later
- `BufferTooLargeByteStreamBufferError`: buffer growth exceeded cap
- `FrameTooLargeByteStreamBufferError`: single frame exceeded size limit
- `OutstandingReserveByteStreamBufferError` / `NoOutstandingReserveByteStreamBufferError`: invalid state transitions

Design choice:
- Limit errors subclass `ValueError`
- State errors subclass `RuntimeError`
- Preserves compatibility while enabling semantic distinction

### Limits
- `max_size` on buffers (optional, default None)
- `max_size` on framers/codecs

These limits are enforced eagerly to prevent memory exhaustion.

---

## 9. Framing & Search

### ScanningByteStreamBuffer A wrapper that caches negative `find()` progress:

**Purpose**
- Optimizes trickle-data scenarios where small writes are repeatedly followed by unsuccessful delimiter searches
- Conservatively caches only negative results for default find range (`start==0, end=None`)
- Prevents re-scanning the same prefix repeatedly

**Design**
- Tracks "scan_from" position per delimiter
- Allows overlap region (`delimiter_length - 1`) to catch matches spanning old/new boundaries
- Adjusts cache on consumption (advance/split_to)

Pairs well with `LongestMatchDelimiterByteStreamFrameDecoder`.

### Longest-match delimiter framing A dedicated codec layer implements:
- Overlapping delimiters (`\r` vs `\r\n`)
- Longest-match semantics
- Deferred emission when ambiguity exists
- Explicit `final=True` flush at EOF

Key insight: > Delimiter resolution must live *above* the buffer but *below* protocol logic.

The buffer's `find/rfind` remain simple, single-needle primitives; framing logic resolves ambiguity.

### Length-field framing (`LengthFieldByteStreamFrameDecoder`)
- Netty-style length-prefixed frame decoding
- Configurable field offset, length (1/2/4/8 bytes), byte order
- Length adjustment and initial byte stripping
- Uses `coalesce()` for efficient header parsing

---

## 10. Binary Read Helpers

Implemented as methods on **`ByteStreamBufferReader`** (a lightweight wrapper around a buffer):
- `peek_exact(n)` / `take(n)` / `read_bytes(n)`
- `peek_u8()` / `read_u8()`
- `peek_u16_be()` / `read_u16_be()` / `peek_u16_le()` / `read_u16_le()`
- `peek_u32_be()` / `read_u32_be()` / `peek_u32_le()` / `read_u32_le()`

All rely on:
- `coalesce(n)` for contiguity
- `advance(n)` for consumption
- `NeedMoreDataByteStreamBufferError` for retry signaling

This keeps the buffer surface small while enabling rich protocol parsing. The reader is a thin adapter; the real work
remains in the buffer.

---

## 11. File-Like Adapters & Interop

Adapters exist to bridge:
- Buffers → file-like readers: `ByteStreamBufferBytesReaderAdapter`
- Buffers → file-like writers: `ByteStreamBufferWriterAdapter`
- BytesIO → buffers: `BytesIoByteStreamBuffer`

**ByteStreamBufferBytesReaderAdapter** properties:
- Policy-driven behavior (`raise`, `return_partial`, `block`)
- Implements `read(n)`, `read1(n)`, `readall()`
- Optional `fill()` callback for blocking mode
- Explicit handling of partial reads and EOF

**ByteStreamBufferWriterAdapter** properties:
- Simple write-through to file-like sink
- Accepts bytes-like and buffer views
- Writes segments without materializing copies when possible

Key design:
- No reliance on `io` abstractions in the core buffer layer
- Explicit handling of `BytesIO.getbuffer()` pinning hazards in `BytesIoByteStreamBuffer`

Interop is intentionally *ugly but isolated*; the core remains clean.

---

## 12. Relation to Other Ecosystems

### Netty
- Netty’s buffer complexity is split across many types (heap, direct, composite)
- This design captures the *behavioral essence* (segmentation, coalescing, stable views) without refcounting

### Tokio / Rust
- Similar semantics exist implicitly (`Buf::chunk`, `advance`)
- Python benefits from explicit coalescing due to higher call overhead

### Twisted / asyncio
- Older designs rely on callbacks and file-like objects
- This system is explicitly designed *post-async/await*, but not dependent on it

---

## 13. What This Enables Next

With the buffer layer stabilized and core framers implemented, higher-level work can proceed safely:
- HTTP/1 streaming parsing
- Binary protocol codecs (using `ByteStreamBufferReader`)
- Pipeline lifecycle (EOF, errors, close)
- Transport drivers (async, sync, custom)
- Additional specialized framers as protocol needs emerge

**Already implemented:**
- Length-prefixed framing (`LengthFieldByteStreamFrameDecoder`)
- Delimiter-based framing with overlap handling (`LongestMatchDelimiterByteStreamFrameDecoder`)
- Binary read helpers (`ByteStreamBufferReader`)
- File-like adapters (`ByteStreamBufferBytesReaderAdapter`, `ByteStreamBufferWriterAdapter`)
- Trickle-data optimization (`ScanningByteStreamBuffer`)

The buffer layer is now considered **foundationally complete**: additional features should be justified by concrete
protocol needs, not speculation.

---

## 14. Key Takeaway

This buffer system is intentionally:
- **Explicit**, not magical
- **Predictable**, not clever
- **Composable**, not monolithic

It trades a small amount of convenience for long-term correctness and clarity — exactly what is needed to support a
robust, Netty-like protocol toolkit in Python.
