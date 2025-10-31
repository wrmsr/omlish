# Overview

Core utilities and foundational code. It's relatively large but completely self-contained, and has **no required
dependencies of any kind**.

# Notable packages

- **[lang](https://github.com/wrmsr/omlish/blob/master/omlish/lang)** - The standard library of this standard library.
  Usually imported as a whole (`from omlish import lang`), it contains an array of general purpose utilities used
  practically everywhere. It is kept relatively lightweight: its heaviest import is stdlib dataclasses and its
  transitives. Some of its contents include:

  - **[cached](https://github.com/wrmsr/omlish/blob/master/omlish/lang/cached)** - The standard `cached_function` /
    `cached_property` tools, which are more capable than
    [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache).
  - **[imports](https://github.com/wrmsr/omlish/blob/master/omlish/lang/imports.py)** - Import tools like:
    - `proxy_import` - For late-loaded imports.
    - `proxy_init` - For late-loaded module globals.
    - `auto_proxy_init` - For automatic late-loaded package exports.
  - **[classes](https://github.com/wrmsr/omlish/blob/master/omlish/lang/classes)** - Class tools and bases, such as
    `Abstract` (which checks at subclass definition not instantiation), `Sealed` / `PackageSealed`, and `Final`.
  - **[maybes](https://github.com/wrmsr/omlish/blob/master/omlish/lite/maybes.py)** - A simple, nestable formalization
    of the presence or absence of an object, as in [many](https://en.cppreference.com/w/cpp/utility/optional)
    [other](https://docs.oracle.com/javase/8/docs/api/java/util/Optional.html)
    [languages](https://doc.rust-lang.org/std/option/).
  - **[maysync](https://github.com/wrmsr/omlish/blob/master/omlish/lite/maysync.py)** - A lightweight means of sharing
    code between sync and async contexts, eliminating the need for maintaining sync and async versions of functions.

- **[bootstrap](https://github.com/wrmsr/omlish/blob/master/omlish/bootstrap)** - A centralized, configurable,
  all-in-one collection of various process-initialization minutiae like resource limiting, profiling, remote debugging,
  log configuration, environment variables, et cetera. Usable as a context manager or via its
  [cli](https://github.com/wrmsr/omlish/blob/master/omlish/bootstrap/main.py).

- **[collections](https://github.com/wrmsr/omlish/blob/master/omlish/collections)** - A handful of collection utilities
  and simple implementations, including:

  - **[cache](https://github.com/wrmsr/omlish/blob/master/omlish/collections/cache)** - A configurable LRU / LFU cache
    with options like ttl and  max size / weight.
  - **[hasheq](https://github.com/wrmsr/omlish/blob/master/omlish/collections/hasheq.py)** - A dict taking an external
    `__hash__` / `__eq__` implementation.
  - **[identity](https://github.com/wrmsr/omlish/blob/master/omlish/collections/identity.py)** - Identity-keyed
    collections.
  - **[sorted](https://github.com/wrmsr/omlish/blob/master/omlish/collections/sorted)** - Interfaces for value-sorted
    collections and key-sorted mappings, and a simple but correct skiplist-backed implementation.
  - **[persistent](https://github.com/wrmsr/omlish/blob/master/omlish/collections/persistent)** - Interfaces for
    [persistent](https://en.wikipedia.org/wiki/Persistent_data_structure) maps, and a simple but correct treap-backed
    implementation.

- **[dataclasses](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses)** - A fully-compatible
  reimplementation of stdlib [dataclasses](https://docs.python.org/3/library/dataclasses.html) with numerous
  enhancements and additional features. The
  [full stdlib test suite](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/tests/cpython) is run against
  it ensuring compatibility - they *are* dataclasses. Current enhancements include:

  - Simple field coercion and validation.
  - Any number of `@dc.init` or `@dc.validate` methods, not just a central `__post_init__`.
  - Optional generic type parameter substitution in generated `__init__` methods, enabling accurate reflection.
  - An optional [metaclass](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/metaclass) which removes the
    need for re-decorating subclasses (with support for inheritance of dataclass parameters like `frozen`), and some
    basic [base classes](https://github.com/wrmsr/omlish/blob/master/omlish/dataclasses/metaclass/bases.py).
  - (Nearly finished) support for ahead-of-time / build-time code generation, greatly reducing import times.

  The stdlib-equivalent api is exported in such a way as to appear to be direct aliases for the stdlib api itself,
  simplifying tool support.

- **[dispatch](https://github.com/wrmsr/omlish/blob/master/omlish/dispatch)** - A beefed-up version of
  [functools.singledispatch](https://docs.python.org/3/library/functools.html#functools.singledispatch), most notably
  supporting MRO-honoring method impl dispatch.

- **[formats](https://github.com/wrmsr/omlish/blob/master/omlish/formats)** - Tools for various data formats, including:

  - **[json](https://github.com/wrmsr/omlish/blob/master/omlish/formats/json)** - Tools for json, including abstraction
    over various backends and a self-contained streaming / incremental parser.
  - **[json5](https://github.com/wrmsr/omlish/blob/master/omlish/formats/json5)** - A self-contained and tested
    [Json5](https://json5.org/) parser.
  - **[toml](https://github.com/wrmsr/omlish/blob/master/omlish/formats/toml)** - Toml tools, including a
    [lite](#lite-code) version of the stdlib parser (for use in older pythons).

- **[http](https://github.com/wrmsr/omlish/blob/master/omlish/http)** - HTTP code, including:

  - **[clients](https://github.com/wrmsr/omlish/blob/master/omlish/http/clients)** - An abstraction over HTTP clients,
    with urllib and httpx implementations.
  - **[coro](https://github.com/wrmsr/omlish/blob/master/omlish/http/coro)** - Coroutine /
    [sans-io](https://sans-io.readthedocs.io/) style reformulation of some stdlib http machinery - namely `http.server`
    (and soon `http.client`). This style of code can run the same in sync, async, or
    [any](https://docs.python.org/3/library/selectors.html)
    [other](https://github.com/wrmsr/omlish/blob/master/omlish/asyncs/bluelet) context.

- **[inject](https://github.com/wrmsr/omlish/blob/master/omlish/inject)** - A
  [guice](https://github.com/google/guice)-style dependency injector.

- **[io](https://github.com/wrmsr/omlish/blob/master/omlish/io)** - IO tools, including:

  - **[compress](https://github.com/wrmsr/omlish/blob/master/omlish/io/compress)** - Abstraction over various
    compression schemes, with particular attention to incremental operation. For example it includes
    [an incremental reformulation of stdlib's gzip](https://github.com/wrmsr/omlish/blob/master/omlish/io/compress/gzip.py).
  - **[coro](https://github.com/wrmsr/omlish/blob/master/omlish/io/coro)** - Utilities for coroutine / sans-io style
    code.
  - **[fdio](https://github.com/wrmsr/omlish/blob/master/omlish/io/fdio)** - An implementation of classic
    [selector](https://docs.python.org/3/library/selectors.html)-style IO dispatch, akin to the deprecated
    [asyncore](https://docs.python.org/3.11/library/asyncore.html). While more modern asyncio style code is generally
    preferred, it nearly always involves
    [background threads](https://github.com/python/cpython/blob/95d9dea1c4ed1b1de80074b74301cee0b38d5541/Lib/asyncio/unix_events.py#L1349)
    making it [unsuitable for forking processes](https://rachelbythebay.com/w/2011/06/07/forked/) like
    [process supervisors](https://github.com/wrmsr/omlish/blob/master/ominfra/supervisor).

- **[jmespath](https://github.com/wrmsr/omlish/blob/master/omlish/specs/jmespath)** - A vendoring of
  [jmespath community edition](https://github.com/jmespath-community/python-jmespath), modernized and adapted to this
  codebase.

- **[marshal](https://github.com/wrmsr/omlish/blob/master/omlish/marshal)** - A
  [jackson](https://github.com/FasterXML/jackson)-style serde system.

- **[manifests](https://github.com/wrmsr/omlish/blob/master/omlish/manifests)** - A system for sharing lightweight
  metadata within / across codebases.

- **[reflect](https://github.com/wrmsr/omlish/blob/master/omlish/reflect)** - Reflection utilities, including primarily
  a formalization of stdlib type annotations for use at runtime, decoupled from stdlib impl detail. Keeping this working
  is notoriously difficult across python versions (one of the primary reasons for only supporting 3.13+).

- **[sql](https://github.com/wrmsr/omlish/blob/master/omlish/sql)** - A collection of SQL utilities, including:

  - **[api](https://github.com/wrmsr/omlish/blob/master/omlish/sql/api)** - An abstracted api for SQL interaction, with
    support for dbapi compatible drivers (and a SQLAlchemy adapter).
  - **[queries](https://github.com/wrmsr/omlish/blob/master/omlish/sql/queries)** - A SQL query builder with a fluent
    interface.
  - **[alchemy](https://github.com/wrmsr/omlish/blob/master/omlish/sql/alchemy)** - SQLAlchemy utilities. The codebase
    has moved away from SQLAlchemy in favor of its own internal SQL api, but it will likely still remain as an optional
    dep for the api adapter.

- **[testing](https://github.com/wrmsr/omlish/blob/master/omlish/testing)** - Test - primarily pytest - helpers,
  including:

  - **['harness'](https://github.com/wrmsr/omlish/blob/master/omlish/testing/pytest/inject/harness.py)** - An all-in-one
    fixture marrying it to the codebase's dependency injector.
  - **[plugins/async](https://github.com/wrmsr/omlish/blob/master/omlish/testing/pytest/plugins/asyncs)** - An in-house
    async-backend abstraction plugin, capable of handling all of asyncio / trio / trio-asyncio /
    *any-future-event-loop-impl* without having multiple fighting plugins (*[I know, I know](https://xkcd.com/927/)*).
  - **[plugins](https://github.com/wrmsr/omlish/blob/master/omlish/testing/pytest/plugins)** - Various other plugins.

- **[lite](https://github.com/wrmsr/omlish/blob/master/omlish/lite)** - The standard library of 'lite' code. This is the
  only package beneath `lang`, and parts of it are re-exported by it for deduplication. On top of miscellaneous
  utilities it contains a handful of independent, self-contained, significantly simplified 'lite' equivalents of some
  major core packages:

  - **[lite/inject.py](https://github.com/wrmsr/omlish/blob/master/omlish/lite/inject.py)** - The lite injector, which
    is more conservative with features and reflection than the core injector. The codebase's
    [MiniGuice](https://github.com/google/guice/commit/70248eafa90cd70a68b293763e53f6aec656e73c).
  - **[lite/marshal.py](https://github.com/wrmsr/omlish/blob/master/omlish/lite/marshal.py)** - The lite marshalling
    system, which is a classic canned setup of simple type-specific 2-method classes and limited generic handling.

# Lite code

A subset of this codebase is written in a 'lite' style (non-'lite' code is referred to as *standard* code). While
standard code is written for python 3.13+, 'lite' code is written for 3.8+, and is written in a style conducive to
[amalgamation](https://github.com/wrmsr/omlish/blob/master/omdev#amalgamation) in which multiple python source files are
stitched together into one single self-contained python script.

Code written in this style has notable differences from standard code, including (but not limited to):

- No name mangling is done in amalgamation, which means (among other things) that code must be written expecting to be
  all dumped into the same giant namespace. Where a standard class might be
  [`omlish.inject.keys.Key`](https://github.com/wrmsr/omlish/blob/master/omlish/inject/keys.py), a lite equivalent might
  be [`omlish.lite.inject.InjectorKey`](https://github.com/wrmsr/omlish/blob/master/omlish/lite/inject.py).
- All internal imports `import` each individual item out of modules rather than importing the modules and referencing
  their contents. Where standard code would `from .. import x; x.y`, lite code would `from ..x import y; y`. As a result
  there are frequently 'api' non-instantiated namespace classes serving the purpose of modules - just handy bags of
  stuff with shortened names.
- As lite code is tested in 3.8+ but core code requires 3.13+, packages containing lite code can't import anything
  standard in their (and their ancestors') `__init__.py`'s. Furthermore, `__init__.py` files are omitted outright in
  amalgamation, so they effectively must be empty in any package containing any lite code. As a result there are
  frequently [`all.py`](https://github.com/wrmsr/omlish/blob/master/omlish/configs/all.py) files in mixed-lite packages
  which serve the purpose of `__init__.py` for standard usage - where importing standard packages from standard code
  would be done via `from .. import lang`, importing mixed-lite packages from standard code would be done via
  `from ..configs import all as cfgs`.

# Dependencies

This library has no required dependencies of any kind, but there are some optional integrations - see
[`__about__.py`](https://github.com/wrmsr/omlish/blob/master/omlish/__about__.py) for a full list, but some specific
examples are:

- **asttokens / executing** - For getting runtime source representations of function call arguments, an optional
  capability of [check](https://github.com/wrmsr/omlish/blob/master/omlish/check.py).
- **anyio** - While lite code must use only asyncio, non-trivial async standard code prefers to be written to anyio.
- **pytest** - What is used for all standard testing - as lite code has no dependencies of any kind its testing uses
  stdlib's [unittest](https://docs.python.org/3/library/unittest.html).
- **wrapt** - For (optionally-enabled) injector circular proxies.
- **sqlalchemy** - The codebase has migrated away from SQLAlchemy in favor of the internal api but it retains it as an
  optional dep to support adapting the internal api to it.

Additionally, some catchall dep categories include:

- **compression** - Various preferred compression backends like lz4, python-snappy, zstandard, and brotli.
- **formats** - Various preferred data format backends like orjson/ujson, pyyaml, cbor2, and cloudpickle.
- **sql drivers** - Various preferred and tested sql drivers.
