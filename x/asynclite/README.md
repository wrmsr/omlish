`asynclite` is an abstraction layer for (possibly async) IO and synchronization operations.

Not unlike `anyio`, it provides an assortment of classes and functions corresponding to a subset of those provided by
its supported backends wrapped in a uniform `async` interface. Unlike `anyio`, one of its backends is `sync` - backed by
non-async operations despite still having an `async` interface - which allows code written once (as async) to be used in
both sync and async contexts.

Additionally compared to `anyio` it provides far less sophisticated abstractions: it intends only to expose a 'lowest
common denominator' of functionality provided by and mapping directly to its backends. It offers none of the higher
level features of `anyio` (such as structured concurrency).

The code is organized into 'slices' corresponding to primitives exposed by the backends: events, locks, queues, sleeps,
and so on. For each 'slice' there is a subclass of `AsyncliteApi`, and may or may not be subclasses of
`AsyncliteObject`. This allows consumers to declare only dependencies on the 'slices' of functionality necessary for
their operation: code requiring only 'sleep' needn't depend on the entire capability set of the system.

Notably, with the exception of the `anyio` backend, this is `@omlish-lite` code, and runs on python 3.8+. Because of
its dependency on `anyio` that subpackage cannot be `@omlish-lite`, but it is still generally written in that style for
consistency with the other backends.
