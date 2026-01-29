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
- Per-buffer `max_bytes`
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

## 4. Two Concrete Buffer Backends

### SegmentedByteStreamBuffer A list-of-segments design (bytes / bytearray chunks):

**Strengths**
- Avoids pathological “large buffer pinned by tiny tail”
- Stable zero-copy views for `split_to`
- Natural fit for network chunking and streaming

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

These two backends intentionally cover different workload shapes; both conform to the same conceptual interface.

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
- `max_bytes` on buffers (optional, default None)
- `max_size` on framers/codecs

These limits are enforced eagerly to prevent memory exhaustion.

---

## 9. Framing & Search

### Longest-match delimiter framing A dedicated codec layer implements:
- Overlapping delimiters (`\r` vs `\r\n`)
- Longest-match semantics
- Deferred emission when ambiguity exists
- Explicit `final=True` flush at EOF

Key insight: > Delimiter resolution must live *above* the buffer but *below* protocol logic.

The buffer’s `find/rfind` remain simple, single-needle primitives; framing logic resolves ambiguity.

---

## 10. Binary Read Helpers

Implemented as **pure functions atop buffers**, not methods:
- `peek_exact`
- `take`
- `read_bytes`
- `read_u8`, `read_u16_be`, `read_u32_le`, etc.

All rely on:
- `coalesce(n)` for contiguity
- `advance(n)` for consumption
- `NeedMoreData` for retry signaling

This keeps the buffer surface small while enabling rich protocol parsing.

---

## 11. File-Like Adapters & Interop

Adapters exist to bridge:
- File-like objects → buffers
- Buffers → file-like readers/writers

Key properties:
- Policy-driven behavior (`raise`, `return_partial`, `block`)
- No reliance on `io` abstractions in the core
- Explicit handling of `BytesIO.getbuffer()` pinning hazards

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

With the buffer layer stabilized, higher-level work can proceed safely:
- Length-prefixed framing
- HTTP/1 streaming parsing
- Binary protocol codecs
- Pipeline lifecycle (EOF, errors, close)
- Transport drivers (async, sync, custom)

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
