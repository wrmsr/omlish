# IO Pipelines

A lightweight, composable pipeline framework for transforming and routing data through chains of handlers. Inspired by
Netty's `ChannelPipeline` architecture, but designed for Python with significant simplifications and adaptations.

## Overview

The pipeline system provides a structured way to process data through an ordered sequence of handlers. Unlike
traditional callback-heavy or inheritance-based approaches, it emphasizes **composition** and **incremental
transformation** of messages flowing through a chain.

**Key characteristics:**

- **Bytes-agnostic core**: Works with any Python objects - bytes, strings, dataclasses, protocol messages, or even
  simple values. Useful for file I/O, network protocols, complex object transformations, or generator pipelines.
- **Embeddable**: Designed for integration into arbitrary Python runtimes - sync, async, threaded, or single-threaded.
  No event loop coupling.
- **Synchronous handlers**: Even in async contexts, handlers themselves are synchronous functions. Async/await exists
  only at the *edges* (in drivers). This keeps the pipeline deterministic, incremental, and testable without I/O.
- **Composable and reusable**: Small, focused handlers can be mixed and matched to build complex processing logic.
- **Explicit flow control**: Built-in support for backpressure, lifecycle signals, and message propagation guarantees.

## Core Concepts

The system is built around three primary abstractions:

### Pipeline (`IoPipeline`)

An ordered chain of handlers with input/output state management. The pipeline:

- Maintains a doubly-linked list of handler contexts
- Manages message flow in both directions (inbound and outbound)
- Tracks lifecycle state (initial input, final input, final output)
- Provides an output queue for messages that complete the outbound journey
- Supports services and metadata for cross-cutting concerns

Unlike Netty, which separates `Channel` and `ChannelPipeline`, this design **fuses them into a single `IoPipeline`**.
This is because much of what would be channel-level concerns are outsourced to external "drivers" - which may be as
simple as a few lines of Python code at the call site.

### Handler (`IoPipelineHandler`)

A composable unit that processes messages flowing through the pipeline. Handlers implement up to three methods:

- `inbound(ctx, msg)` - Process messages flowing inward (toward the pipeline's innermost position)
- `outbound(ctx, msg)` - Process messages flowing outward (toward the pipeline's outermost position)
- `notify(ctx, notification)` - Receive directionless notifications (e.g., handler added/removed)

Unlike Netty's extensive handler interface with many specialized methods (`channelActive`, `channelRead`,
`channelReadComplete`, `write`, `flush`, `close`, etc.), this design **collapses everything into just three methods**.
This simplification is possible because:

- Lifecycle events are represented as special message types (e.g., `InitialInput`, `FinalInput`, `FinalOutput`)
- Flow control is message-based rather than method-based
- The smaller scope of use cases doesn't require the same level of granularity

Handlers can be **unique** (only one instance per pipeline) or **shareable** (same instance at multiple positions).

### Context (`IoPipelineHandlerContext`)

The embodiment of a handler instance at a specific position in a pipeline. The context provides:

- `feed_in(msg)` - Send a message to the next inbound handler
- `feed_out(msg)` - Send a message to the next outbound handler
- `defer(fn)` - Schedule deferred execution with completion tracking
- `storage` - Per-handler-position storage for stateful processing
- Access to the pipeline, services, and handler reference

Contexts are **private** to a handler and should never be cached or shared. They become invalidated when the handler is
removed from the pipeline.

## Message Flow

Messages flow through the pipeline in two directions:

**Inbound** (outer → inner):
```
Pipeline.feed_in() → Handler₀.inbound() → Handler₁.inbound() → ... → Handlerₙ.inbound() → Terminal
```

**Outbound** (inner → outer):
```
Context.feed_out() → Handlerₙ.outbound() → ... → Handler₁.outbound() → Handler₀.outbound() → Pipeline.output
```

Handlers can:
- Transform messages and forward them: `ctx.feed_in(transform(msg))`
- Generate multiple messages from one: call `feed_in()` multiple times
- Drop messages: simply don't forward them (unless they're `MustPropagate`)
- Convert between directions: receive inbound, send outbound (e.g., for request/response patterns)

## Special Message Types

The system defines several message types with special semantics:

- **`InitialInput`**: Signals the start of inbound data (analogous to "connected"). Must propagate fully.
- **`FinalInput`**: Signals the end of inbound data (analogous to "EOF"). Must propagate fully.
- **`FinalOutput`**: Signals the end of outbound data (analogous to "close"). Must propagate fully.
- **`Error`**: Wraps exceptions that occurred during processing, includes direction and handler reference.
- **`Defer`**: Represents deferred work with completion tracking and optional message pinning.
- **`MustPropagate`**: Base class for messages that must be seen at their terminal position (enforced by object
  identity).
- **`MayPropagate`**: Messages that may be silently dropped at terminal positions.

## Example Usage

### Basic Pipeline

```python
import typing as ta

from omlish.io.pipelines.core import IoPipeline
from omlish.io.pipelines.core import IoPipelineHandler
from omlish.io.pipelines.core import IoPipelineHandlerContext

class IntIncrementHandler(IoPipelineHandler):
    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, int):
            msg += 1
        ctx.feed_in(msg)

class IntToStrHandler(IoPipelineHandler):
    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, int):
            msg = str(msg)
        ctx.feed_in(msg)

class OutputStrHandler(IoPipelineHandler):
    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, str):
            ctx.feed_out(msg)
            return
        ctx.feed_in(msg)

# Create pipeline with handlers
pipeline = IoPipeline.new([
    IntIncrementHandler(),
    IntToStrHandler(),
    OutputStrHandler(),
])

# Feed messages
pipeline.feed_in(42)
result = pipeline.output.poll()  # '43'
```

### Dynamic Handler Management

```python
# Add handlers dynamically
ref = pipeline.add_outermost(SomeHandler(), name='special')

# Remove by reference
pipeline.remove(ref)

# Replace handlers
pipeline.replace(old_ref, NewHandler())

# Find handlers
ref = pipeline.handlers_by_name()['special']
refs = pipeline.find_handlers_of_type(IntIncrementHandler)
```

## Differences from Netty

While inspired by Netty's architecture, this implementation diverges in several important ways:

1. **Fused Channel and Pipeline**: Netty separates `Channel` (I/O abstraction) and `ChannelPipeline` (handler chain).
   Here, they're fused into `IoPipeline` because driver concerns are external and often trivial.

2. **Bytes-agnostic**: Netty is fundamentally oriented around `ByteBuf` and network I/O. This implementation works with
   arbitrary Python objects and is useful in much smaller contexts - file I/O, object transformations, in-memory
   processing, or even complex generators.

3. **Simplified Handler Interface**: Netty has many specialized handler methods. This collapses to just `notify`,
   `inbound`, and `outbound`, with lifecycle and flow control expressed as messages.

4. **No Event Loop Coupling**: Netty is tightly integrated with its event loop. This is runtime-agnostic and can be
   driven synchronously, from threads, from asyncio, or from other async frameworks.

5. **Python-native Patterns**: Uses dataclasses for messages, context managers for lifecycle, and Pythonic APIs rather
   than direct Java ports.

6. **Smaller Scope**: Designed for embedding and composition rather than being a full networking framework. The focus
   is on the pipeline abstraction itself.

## Additional Components

Beyond the core pipeline abstraction, the package includes:

- **Byte stream handlers**: Helpers for working with byte streams, including buffering, framing, and decoding
  (built on top of `omlish.io.streams`)
- **Services**: Cross-cutting pipeline concerns like async/await integration, task scheduling, and cooperative yielding
- **Flow control**: Backpressure and readiness signaling for producers and consumers (implemented as a service)
- **Metadata**: Type-safe attachment of configuration or context to pipelines

These components build on the core abstractions but are entirely optional - the core pipeline can be used standalone
for any message transformation use case.
