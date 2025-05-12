# Overview

Core utilities and foundational code. It's relatively large but completely self-contained.

# Notable packages

- **[lang](lang)** - The standard library of this standard library. Usually imported as a whole
  (`from omlish import lang`), it contains an array of general purpose utilities used practically everywhere. It is kept
  relatively lightweight: its heaviest import is stdlib dataclasses and its transitives. Some of its contents include:

  - **[cached](lang/cached)** - The standard `cached_function` / `cached_property` tools, which are more capable than
    [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache).
  - **[imports](lang/imports.py)** - Import tools like `proxy_import` for late-loaded imports and `proxy_init` for
    late-loaded module globals.
  - **[classes](lang/classes)** - Class tools and bases, such as `Abstract` (which checks at subclass definition not
    instantiation), `Sealed` / `PackageSealed`, and `Final`.
  - **[maybes](lang/maybes.py)** - A simple, nestable formalization of the presence or absence of an object, as in
    [many](https://en.cppreference.com/w/cpp/utility/optional)
    [other](https://docs.oracle.com/javase/8/docs/api/java/util/Optional.html)
    [languages](https://doc.rust-lang.org/std/option/).

- **[bootstrap](bootstrap)** - A centralized, configurable, all-in-one collection of various process-initialization
  minutiae like resource limiting, profiling, remote debugging, log configuration, environment variables, et cetera.
  Usable as a context manager or via its [cli](bootstrap/main.py).

- **[collections](collections)** - A handful of collection utilities and simple implementations, including:

  - **[cache](collections/cache)** - A configurable LRU / LFU cache with options like ttl and  max size / weight.
  - **[hasheq](collections/hasheq.py)** - A dict taking an external `__hash__` / `__eq__` implementation.
  - **[identity](collections/identity.py)** - Identity-keyed collections.
  - **[sorted](collections/sorted)** - Interfaces for value-sorted collections and mappings, and a simple but correct
    skiplist-backed implementation.
  - **[persistent](collections/persistent)** - Interfaces for
    [persistent](https://en.wikipedia.org/wiki/Persistent_data_structure) maps, and a simple but correct treap-backed
    implementation.

- **[dataclasses](dataclasses)** - A fully-compatible reimplementation of stdlib
  [dataclasses](https://docs.python.org/3/library/dataclasses.html) with numerous enhancements and additional features.
  The [full stdlib test suite](dataclasses/tests/cpython) is run against it ensuring compatibility - they *are*
  dataclasses. Current enhancements include:

  - Simple field coercion and validation.
  - Any number of `@dc.init` or `@dc.validate` methods, not just a central `__post_init__`.
  - Optional generic type parameter substitution in generated `__init__` methods, enabling accurate reflection.
  - An optional [metaclass](dataclasses/metaclass) which removes the need for re-decorating subclasses (with support for
    inheritance of dataclass parameters like `frozen`), and some basic [base classes](dataclasses/metaclass/bases.py).
  - (Nearly finished) support for ahead-of-time / build-time code generation, greatly reducing import times.

  The stdlib-equivalent api is exported in such a way as to be direct aliases for the stdlib api itself, simplifying
  tool support.

- **[dispatch](dispatch)** - A beefed-up version of
  [functools.singledispatch](https://docs.python.org/3/library/functools.html#functools.singledispatch), most notably
  supporting MRO-honoring method impl dispatch.

- **[formats](formats)** - Tools for various data formats, including:

  - **[json](formats/json)** - Tools for json, including abstraction over various backends and a self-contained
    streaming / incremental parser.
  - **[json5](formats/json5)** - A self-contained and tested [Json5](https://json5.org/) parser.
  - **[toml](formats/toml)** - Toml tools, including a [lite](#lite-code) version of the stdlib parser (for use in older
    pythons).

- **[http](http)** - HTTP code, including:

  - **[clients](http/clients)** - An abstraction over HTTP clients, with urllib and httpx implementations.
  - **[coro](http/coro)** - Coroutine / [sans-io](https://sans-io.readthedocs.io/) style reformulation of some stdlib
    http machinery - namely `http.server` (and soon `http.client`). This style of code can run the same in sync, async,
    or [any](https://docs.python.org/3/library/selectors.html) [other](asyncs/bluelet) context.

- **[inject](inject)** - A [guice](https://github.com/google/guice)-style dependency injector.

- **[io](io)** - IO tools, including:

  - **[compress](io/compress)** - Abstraction over various compression schemes, with particular attention to incremental
    operation. For example it includes [an incremental reformulation of stdlib's gzip](io/compress/gzip.py).
  - **[coro](io/coro)** - Utilities for coroutine / sans-io style code.
  - **[fdio](io/fdio)** - An implementation of classic [selector](https://docs.python.org/3/library/selectors.html)-style
    IO dispatch, akin to the deprecated [asyncore](https://docs.python.org/3.11/library/asyncore.html). While more
    modern asyncio style code is generally preferred, it nearly always involves
    [background threads](https://github.com/python/cpython/blob/95d9dea1c4ed1b1de80074b74301cee0b38d5541/Lib/asyncio/unix_events.py#L1349)
    making it [unsuitable for forking processes](https://rachelbythebay.com/w/2011/06/07/forked/) like
    [process supervisors](https://github.com/wrmsr/omlish/tree/master/ominfra/supervisor).

- **[jmespath](specs/jmespath)** - A vendoring of
  [jmespath community edition](https://github.com/jmespath-community/python-jmespath), modernized and adapted to this
  codebase.

- **[marshal](marshal)** - A [jackson](https://github.com/FasterXML/jackson)-style serde system.

- **[manifests](manifests)** - A system for sharing lightweight metadata within / across codebases.

- **[reflect](reflect)** - Reflection utilities, including primarily a formalization of stdlib type annotations for use
  at runtime, decoupled from stdlib impl detail. Keeping this working is notoriously difficult across python versions
  (one of the primary reasons for only supporting 3.12+).

- **[sql](sql)** - A collection of SQL utilities, including:

  - **[alchemy](sql/alchemy)** - SQLAlchemy utilities. The codebase is moving away from SQLAlchemy however in favor of
    its own internal SQL api.
  - **[api](sql/api)** - An abstracted api for SQL interaction, with support for dbapi compatible drivers (and a 
    SQLAlchemy adapter).
  - **[queries](sql/queries)** - A SQL query builder with a fluent interface.

- **[testing](testing)** - Test - primarily pytest - helpers, including:

  - **['harness'](testing/pytest/inject/harness.py)** - An all-in-one fixture marrying it to the codebase's dependency
    injector.
  - **[plugins/async](testing/pytest/plugins/asyncs)** - An in-house async-backend abstraction plugin, capable of
    handling all of asyncio / trio / trio-asyncio / *any-future-event-loop-impl* without having multiple fighting
    plugins (*[I know, I know](https://xkcd.com/927/)*).
  - **[plugins](testing/pytest/plugins)** - Various other plugins.

- **[lite](lite)** - The standard library of 'lite' code. This is the only package beneath `lang`, and parts of it are
  re-exported by it for deduplication. On top of miscellaneous utilities it contains a handful of independent,
  self-contained, significantly simplified 'lite' equivalents of some major core packages:

  - **[lite/inject.py](lite/inject.py)** - The lite injector, which is more conservative with features and reflection
    than the core injector. The codebase's
    [MiniGuice](https://github.com/google/guice/commit/70248eafa90cd70a68b293763e53f6aec656e73c).
  - **[lite/marshal.py](lite/marshal.py)** - The lite marshalling system, which is a classic canned setup of simple
    type-specific 2-method classes and limited generic handling.

# Lite code

A subset of this codebase is written in a 'lite' style. While most of the code is written for python 3.12+, 'lite' code
is written for 3.8+, and is written in a style conducive to
[amalgamation](https://github.com/wrmsr/omlish/tree/master/omdev#amalgamation) in which multiple python source files are
stitched together into one single self-contained python script.

Code written in this style has notable differences from standard code, including (but not limited to):

- No name mangling is done in amalgamation, which means (among other things) that code must be written expecting to be
  all dumped into the same giant namespace. Where a non-lite class might be [`omlish.inject.keys.Key`](inject/keys.py),
  a lite equivalent might be [`omlish.lite.inject.InjectorKey`](lite/inject.py).
- All internal imports `import` each individual item out of modules rather than importing the modules and referencing
  their contents. Where non-lite code would `from .. import x; x.y`, lite code would `from ..x import y; y`. As a result
  there are frequently 'api' non-instantiated namespace classes serving the purpose of modules - just handy bags of
  stuff with shortened names.
- As lite code is tested in 3.8+ but core code requires 3.12+, packages containing lite code can't import anything
  non-lite in their (and their ancestors') `__init__.py`'s. Furthermore, `__init__.py` files are omitted outright in
  amalgamation, so they effectively must be empty in any package containing any lite code. As a result there are
  frequently [`all.py`](configs/all.py) files in mixed-lite packages which serve the purpose of `__init__.py` for
  non-lite usage - where importing non-lite packages from non-lite code would be done via `from .. import lang`,
  importing mixed-lite packages from non-lite code would be done via `from ..configs import all as cfgs`.

# Dependencies

This library has no required dependencies of any kind, but there are numerous optional integrations - see
[`__about__.py`](__about__.py) for a full list, but some specific examples are:

- **anyio** - While lite code must use only asyncio, non-trivial async non-lite code prefers to be written to anyio.
- **pytest** - What is used for all non-lite testing - as lite code has no dependencies of any kind its testing uses
  stdlib's [unittest](https://docs.python.org/3/library/unittest.html).
- **asttokens / executing** - For getting runtime source representations of function call arguments, an optional
  capability of [check](check.py).
- **wrapt** - For (optionally-enabled) injector circular proxies.
- **greenlet** - For some gnarly stuff like the [sync<->async bridge](asyncs/bridge.py) and the
  [io trampoline](io/trampoline.py).
- **sqlalchemy** - Parts of the codebase use SQLAlchemy for db stuff, but it is being migrated away from in favor of the
  internal api. It will however likely still remain as an optional dep for the api adapter.

Additionally, some catchall dep categories include:

- **compression** - Various preferred compression backends like lz4, python-snappy, zstandard, and brotli.
- **formats** - Various preferred data format backends like orjson/ujson, pyyaml, cbor2, and cloudpickle.
- **sql drivers** - Various preferred and tested sql drivers.
