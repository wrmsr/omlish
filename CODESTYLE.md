### Environment

- Target cpython 3.13 - use the modern language and library features it includes.
  - \[**lite**\] The exception is 'lite' code, which targets python 3.8.
  - **A module is declared as being lite by having a `# @omlish-lite` comment at the top of it, or at the top of any
    `__init__` module in its or any ancestor's package.**
  - As a reminder, non-\[**lite**\] core is referred to as 'standard' code.
- Code should run on modern macOS and Linux - Windows support is not necessary, but still prefer things like
  `os.path.join` over `'/'.join` where reasonable.


### Dependencies

- Outside of a few specific subpackages (and test code), there are no external dependencies of any kind to rely on. Use
  the standard library liberally, use `omlish` for everything else.

- All external runtime dependencies are optional, and generally fit into the following categories:
  - Cryptography: `cryptography`. Its use is optional.
  - File formats: `orjson`, `pyyaml`, `cbor2`, `lxml`, `cloudpickle`, etc. Wherever possible, they serve only as
    accelerators and their absence will not block functionality - code should strive to have internal fallbacks that
    prefer correctness to speed.
  - Text formats: `jinja2`, `markdown-it-py`, etc. Particularly in LLM stuff the full versions of these are unavoidable,
    but simplified internal 'equivalents' exist for simpler usecases.
  - Compression algorithms: `lz4`, `zstandard`, `python-snappy`, `brotli`, etc. These generally have no internal
    fallback if not present in the standard library, but are usually optional at runtime in practice.
  - Database drivers: `pg8000`, `psycopg`, `psycopg2`, `mysql-connecteor-python`, `mysqlclient`, `pymysql`,
    `snowflake-connector-python`, `duckdb`, etc. These also generally have no internal fallback.
  - Large <span aria-label="math">m̶̡̢̡̢̠̥͎͇̯̥̹̪͇͇͇̺̟͋̓͂̇͝͝a̴̧̛̞̾̊͒̈́̿͗̓̐̊͝t̸̥͖͂̀̆͛́̅́͝͠ȟ̴̢͎͙͍̱̒͂́̆̽̽̈́͝</span>
    libraries: `numpy`, `torch`, `mlx`, `tinygrad`, `transformers`, `llama-cpp-python`, `tokenizers`, etc. These tend to
    have gigantic interface surface areas compared to the previous categories, and all interaction them is heavily
    quarantined to a single isolated package per dependency. Outside of these isolated packages they absolutely cannot
    be assumed to be present.
  - `textual`, specifically - it is the sole chosen TUI library. Almost all terminal functionality throughout the
    codebase is usable without it - it only powers a small number of specific, larger TUI apps.
  - Async backends: `trio`, `anyio`, `trio-asyncio`. Except in specific situations (such as under `textual`) async code
    is not assumed to be running under asyncio, and in general async code should use anyio.
    - **NOTE:** this is in flux.
  - The 'hyper stack' for production web serving: `h11`, `h2`, `wsproto`. There are simpler internal http servers for
    local and development use.
  - Unique, focused, irreproducible, core utility libraries: `executing` / `asttokens`, `greenlet`, `wrapt`.  In general
    'core' utility libraries are either avoided, replaced with an equivalent internal implementation, or in small cases
    (often for \[**lite**\] code) vendored (preserving licenses, copyrights, and attribution) such as in parts of
    `omdev.packaging`. However, there is a small number of libraries that do things I have absolutely no interest in
    attempting or maintaining myself, such as those listed here. As with all other deps these are strictly optional, and
    fallbacks exist wherever possible.
  - `httpx` specifically. It is **NOT** required - various internal async http client options exist. It is however an
    optional integration.
  - Various other optional backends: `psutil`, `mwparserfromhell`, `regex`, `ddgs`, `tree-sitter`, etc.
- Notably absent from this list:
  - `pydantic`. Use dataclasses.
  - `click`. Use argparse.
  - Any 'web client' library: `boto3`, `google-api-python-client`, `openai`, `anthropic`, etc. These are not used, even
    optionally, in the codebase. All interaction with such api's is done with internal clients, usually via dataclasses.
    - Note: references to boto exist in code but only for code generation and cross-validation testing. Boto is not used
      for production aws interaction.
  - `gitpython`, `docker`, etc. Drive their cli's through a subprocess or talk to the api through the socket.
  - `rich` (outside of `textual`). Use `omlish.term`, or simple inline escape codes, or just output plain text.
  - `loguru` / `logbook` / `structlog`. Use `omlish.logs` or just stdlib `logging`.
  - `json5`. Use `omlish.formats.json5`.
  - Various specs: `jsonrpc`, `jsonschema`, `openapi`, `mcp`. Internal implementations exist.
  - Web frameworks: `flask`, `fastapi`, `starlette`, etc. Equivalent internal patterns exist.


### Structure

- In general, strongly prefer clusters of small source files to a single or small number of large ones - a few hundred
  lines of code is a good target maximum, and there is no minimum.
  - Our code is 'type-heavy', and small modules defining nothing but interrelated stateless structures are welcome.
- While not necessarily the case, organize packages as if it were to be managed by a guice-style dependency injector,
  with package-level injector modules that each refer to their child packages' injector modules and so on.
- With the exception of root packages (`om*` directories), (relatively) deep package nesting is preferred over large
  flat packages with many, less tightly related modules.
- Structurally quarantine all interaction with any external dependencies.
  - For small, simple integrations, it may be done within a single module as an optional implementation of an interface
    (or simple function conforming to a signature)
  - For intermediate integrations, prefer a separate module dedicated to that integration.
  - For large, complex integrations, prefer a more root-level package for that integration, whose internal structure
    mirrors that of the core code it's being integrated with.
- In general the structure should mirror a 'Clean' or 'Hexagonal' architecture:
  > Source code dependencies can only point inwards. Nothing in an inner circle can know anything at all about something
    in an outer circle.


### Naming

- Module names should be nouns (usually plural or gerunds), not verbs, so as to not clash with function names. A module
  should be named `parsing.py`, not `parse.py`, so `__init__.py` could `from .parsing import parse` without shadowing
  the module itself.
- Function names should be verbs.
- When naming interface classes, the interface should be the 'bare' name, and implementations should have prefixes and
  suffixes. For example, a user service interface would be `UserService`, with a `DbUserService` or `DictUserService`
  subclass, or even a `UserServiceImpl` subclass if there is only one sensible initial implementation but it still
  justifies being abstracted.
- When using acronyms, only the first letter of the acronym should be uppercased when it appears in CamelCased names so
  as to distinguish it from adjacent acronyms. For example, a class to parse ABNF grammars would be `AbnfParser`, and a
  class to parse the JSON ABNF grammar would be `JsonAbnfParser`.


### Packages

  - All packages must have an `__init__.py` file, even if empty.


### Imports

- **Always** use relative imports within a package. **Never** reference the name of the root package from within itself.
  For example, within the `omlish` package, it's `from . import lang`, not `from omlish import lang`. Within the
  `omlish` root package there should never be an import line containing the word `omlish` - and references to the root
  name should be avoided in general.
- Use the following import aliases for the following modules if they are used:
  - `import dataclasses as dc`
  - `import typing as ta`
- For *package-internal* imports, almost always import specific items rather than whole modules or packages.
  - Here, 'package-internal' is loosely defined as the layer which 'external' users of the code will treat as the
    'public' interface.
- For other imports, strongly prefer to import a module or package, rather than importing specific items from it. So for
  example, use `import typing as ta; fn: ta.Callable ...` as opposed to `from typing import Callable; fn: Callable ...`,
  and `import dataclasses as dc; @dc.dataclass() ...` as opposed to `from dataclasses import dataclass; @dataclass()
  ...`.
- Unless instructed or unavoidable, prefer to use only the standard library and the current existing codebase.
  - Notable exceptions include:
    - anyio - In general async code should write to anyio rather than asyncio (or trio) unless it is specifically being
      written for a particular backend.
      - **NOTE:** this is in flux.
    - pytest - Write tests in pytest-style, and assume it is available.
  - \[**lite**\] 'lite' code can have no external dependencies of any kind, and can only reference other 'lite' code.
    - Lite async code uses only asyncio, and only uses functionality available in python 3.8.
    - Lite tests are written with the unittest package.
- Unless forced to for external interoperability, avoid `pathlib` - use `os.path` instead.
- For heavy or optional imports, **ALWAYS** import whole modules, **not** individual module contents. For example, use
  `import torch; t = torch.Tensor(...` rather than `from torch import Tensor; t = Tensor(...`.
  - Rationale: we have a lazy import mechanism that operates at the module level. Do not attempt to manually late-import
    such libraries, just import them as regular modules.


### Modules

- Avoid global state in general. Constants are however fine.
- Do basically no 'work' in module body:
  - *NEVER* eagerly do any IO in module body - wrap any such things in a `@lang.cached_function`.
  - *NEVER* write dumb python 'scripts'. Modules intended as entrypoints are great, but *ALWAYS* make them importable
    side-effect-free, and *ALWAYS* have an `if __name__ == '__main__'` guard at the bottom. And almost always have that
    just call a `def _main() -> None:` or `async def _a_main() -> None:`. Don't pollute module globals with state even
    if the module is running as entrypoint.
- Avoid temporary values in module global scope - for example, construction of a global effectively const `Mapping` via
  a comprehension is fine in module body (as comprehension variables do not leak out to parent scope), but a bare for
  loop in module body is not okay (as the loop variables and any intermediates in the loop body will be left as
  globals). Instead, prefer to define and call a module private function which returns the desired global value.
- Always use relative imports even in python modules intended to be directly executed. All python invocations will
  always be done via `python -m`.


### Classes

- Ensure constructors call `super().__init__()`, even if they don't appear to inherit from anything at their definition
  - *except* if the class is `@ta.Final` and there is explicit reason to not.
  - A blank line should follow the super call if it is the first statement of the method (which it usually is) and there
    are more statements in the method.
- Prefer to use dataclasses for even moderately complex usecases - if there are, say, more than a 2-element tuple, a
  dataclass should probably be used.
- `ta.NamedTuple` still has limited usecases, such as replacing a function's return type from an anonymous tuple to a
  named one (to allow it to be destructured by callers as before), or as a cache key, but in general almost always
  prefer dataclasses.
- If a number of related functions are passing around a growing number of the common args/kwargs, don't be shy about
  refactoring them into methods on a common class with shared immutable and mutable state - if the class is considered
  private implementation detail and not part of any public api.
- For any necessary global state involving multiple interrelated variables, consider encapsulating it in a class, even
  if it's only a private singleton.
- If appropriate, lean towards stateless classes, taking dependencies as constructor arguments and not mutating them
  once set, and passing around and returning dataclasses for intermediate data. If however significant mutable shared
  state is involved just use regular private class fields.
  - Such dependencies should not be exposed publicly for other code to lazily piggyback off of: avoid transitive
    dependencies.
- While not necessarily the case, write code as if it were to be managed by a constructor-injecting guice-style
  dependency injector.
  - Ideally, classes have their functional dependencies as ctor kwargs, and if possible these have sensible defaults.
  - In such cases, prefer to have a kwarg default value for primitives and immutable values, otherwise prefer an ` |
    None = None` kwarg and instantiate the default value in the ctor if necessary.
- Strongly prefer composition over inheritance.
- Prefer relatively fine-grained dependency decomposition.
- **STRONGLY** avoid giant, monolithic classes containing _eVeRyThInG_ anyone will ever need. Avoid classes like
  `AppContext` and `AppConfig` each having large number of fields, *even if* those fields are arbitrarily deeply nested
  within otherwise well-typed child objects.
- For situations in which different behaviors are necessary, prefer to define an interface or abstract class with
  `@abc.abstractmethod` members, and write multiple implementations of them as warranted. Prefer to refer to the
  interface in type annotations unless it must specifically refer to a given implementation.
- Protocols are to be used sparingly where they make sense. In general, nominal typing is a good thing - it is desirable
  that not all functions that return an `int` are `UserIdProvider`'s.
- An abstract class with nothing but abstract (or constant) members is referred to as an interface. In general, prefer
  pure interfaces as opposed to full abstract classes containing partial implementations at package public interface
  boundaries.
- Do not use `abc.ABC` - in standard code use `lang.Abstract` and in lite code use `omlish.lite.abstract.Abstract`.
  - Rationale: `abc.ABCMeta` adds extreme overhead to `isinstance` / `issubclass` checks (6x) in order to support
    virtual base classes, which are almost never needed or desirable.
- Abstract methods should always do nothing but `raise NotImplementedError` - but they *must* do that.
- Properties should be free of side-effects.
  - Rationale: Many utilities eagerly inspect properties at runtime, even private (underscore-prefixed) ones, so they
    cannot alter state.
- Outside of rare, specific instances, **DO NOT** expose mutable internal class state.
  - Keep all mutable state private as single-underscore-prefixed fields.
  - As necessary for usage, expose internal state via methods or `@property`'s. For such cases do one of the following:
    - Type-annotate the return type as immutable. For example, a property exposing an internal `list[int]` would be
      annotated as returning a `ta.Sequence[int]`, and a `dict[int, str]` would be annotated as returning a
      `ta.Mapping[int, str]`.
    - Return a defensive copy of the internal state. For example, a property returning an internal `list[int]` would
      return a copy of the internal list.


### Dataclasses

- Do not use bare, un-called `@dc.dataclass` as a decorator - always use `@dc.dataclass()` even if it is given no
  arguments.
- **Strongly** prefer frozen dataclasses.
- In standard code, prefer to `from omlish import dataclasses as dc` - not the standard library `dataclasses` module.
  The interface and behavior is the same.


### Exceptions

- **Never** use the `assert` statement anywhere but test code - rather, check a condition and raise an `Exception` if
  necessary.
  - Prefer to use the 'check' system (`from omlish import check`, or `from omlish.lite.check import check` for lite
    code) where `assert` would otherwise be used.
- Outside of `TypeError`, `ValueError`, and `RuntimeError`, prefer to create custom subclasses of `Exception` for more
  specific errors. Use inheritance where beneficial to communicate subtypes of errors. Semantically meaningful error
  types are usually more important than human readable error messages.
  - `KeyError` should however not be raised except in the specific and rare case of implementing a `ta.Mapping` or
    direct equivalent. For example, a `UserService` `get_user` method should raise a `UserNotFoundError`, not
    `KeyError`, when a given user is not found.
- In general, avoid use of `contextlib.suppress` - prefer to use an explicit `try`/`except` block instead.


### Type Annotation

- Type annotate functions and class fields wherever possible, even if it is simply `ta.Any`, but use the most specific
  annotation feasible.
  - Lack of type annotation is an explicit choice communicating that that particular code cannot or should not be
    statically typed (usually because it is particularly dynamic).
  - Almost always, if one class field or function parameter is annotated, all fields / parameters / return values should
    be.
  - Return value annotations should be included on most magic methods like `__init__` and `__hash__`, but trickier ones
    like `__exit__` and `__eq__` may be omitted.
  - An exception to this is test code - in general don't bother type annotating test code, and in fact avoid test
    function parameter annotations due to the dynamic nature of pytest fixtures.
- In standard code, use PEP-585 style annotations for builtin types - use `list[int]` instead of `ta.List[int]`, and
  `int | None` instead of `ta.Optional[int]`.
  - Note that \[**lite**\] code must still use pre-PEP-585 annotations like `ta.List[int]` and `ta.Optional[int]` due to
    PEP-585 not being supported in python 3.8. Note that when doing this source files must `# ruff: noqa: ...` any
    relevant lint errors - usually things lke UP006, UP007, UP045, ...
- Use `typing` aliases for non-builtin types - use `ta.Sequence[int]` instead of `collections.abc.Sequence[int]`.
- Prefer to accept immutable, less-specific types - a function should likely use a `ta.Sequence[int]` parameter rather
  than a `list[int]`. Use `ta.AbstractSet` over `set` and `frozenset`, and use `ta.Mapping` over `dict`, accordingly.
- When returning values, prefer to use the full type if the caller 'owns' the value, and use a less-specific, usually
  immutable type when the caller does not. For example, a utility function filtering out odd numbers from a
  `ta.Iterable[int]` can return a new `list[int]`, but a getter property on a class exposing some internal set of
  integers should probably return a `ta.AbstractSet[int]` rather than a `set[int]`.
- Don't avoid `ta.Generic` and type parameters where it makes sense, but usually annotating something as a superclass
  will suffice. When present in a class definition, `ta.Generic` should be the last class in the base class list.
- Do **NOT** use PEP-695 style type parameter syntax yet:
  - Continue to declare `ta.TypeVar`'s explicitly at the top of the module.
  - Continue to declare type aliases as global variables (whose own type is annotated as `ta.TypeAlias`). For example,
    do `IntList: ta.TypeAlias = list[int]`, not `type IntList = list[int]`.
    - Note that in \[**lite**\] code, there is no `ta.TypeAlias` yet (as it was added in 3.10). In lite code, suffix the
      line with `# ta.TypeAlias`. Additionally, type aliases in lite code **must be kept on a single line**. This
      restriction does not apply to standard code.
    - Rationale: lite code is written to be 'amalgamated' - stitched together into a single python file - in which case
      type aliases are relocated to the top of the file **and globally deduplicated**. As such each line of type alias
      must be self-contained.
  - Rationale: the `type` statement produces radically different and incompatible reflective behavior at runtime, and in
    general tools still struggle with the new syntax.


### Comments

- Avoid unnecessary and frivolous comments. Most semantic meaning should be able to be inferred from package / module /
  type / method / function / parameter names and annotations. For example a function like `def add_two_floats(x: float,
  y: float) -> float:` does not need a docstring or comments.
- Do not repeat typing information in function docstrings. In general function and parameter names and types should be
  clear enough to not require explicitly listing them in docstrings. Do not use google-style or equivalent docstrings.
- Both opening and closing docstring triple-quotes should be alone on their own dedicated line *unless* the entire
  docstring (including triple-quotes and indentation) fits on a single 120-column wide line.
- All docstrings should be followed by a blank line.
- Reserve inline comments for 'surprising' or dangerous things, such as invariants which must be maintained. A comment
  like `self._ensure_user_exists()  # ensure user exists` is worthless, but a comment like `self._ensure_user_exists()
  # safe because we already hold the user lock` is valuable.


### Documentation

- Documentation should be written in markdown, and should have a general maximum line width of 120 characters.
- Substantial packages should have a `README.md` file at the root of the package directory outlining the package's
  purpose, usage, and high level architecture. These files are automatically included in distributions as resources for
  end-users.
  - This is however a work in progress ☺️.


### Tests

- As above, write tests in pytest-style.
- Use raw assertions liberally in tests, and use pytest utilities like `pytest.raises`.
- Use fixtures and other advanced pytest features sparingly. Prefer to simply instantiate test data rather than wrap it
  in a fixture.
- In \[**lite**\] test code the `unittest` package must be used instead of `pytest` because lite tests are run in venvs
  with no external dependencies present.
  - Be sure async tests are put in a `IsolatedAsyncioTestCase` subclass.
  - It is equally fine to use both bare `assert` statements and `unittest` assert helpers like `assertCountEqual`.
- In general, prefer to write tests in a way that they can be run in parallel.
- Avoid mocks - prefer to structure code such that a 'simple' but still functioning implementation of an interface can
  be used where a mock would otherwise. For example, for a some `UserService` interface with an `add_user` method, for
  which a `RemoteUserService` would usually make a remote service call, prefer to implement a `DictUserService` class
  with an `add_user` method such that it actually stores the added user in a dictionary on the instance.
  - In practice these are usually useful to have outside of test code as default implementations anyway!
  - These are often called 'fakes' but the term is avoided to emphasize their general non-test utility.
- Strongly avoid monkeypatching anything. Ideally code should be structured to allow more graceful means of
  instrumentation and fault injection (e.g. via alternative interface implementations).
  - Occasional unavoidable exceptions exist, such as being forced to patch an external dep, or when doing fault
    injection that's too fine-grained to justify interface decomposition.
- An ideal to aim for is a test suite reproducing all realistic (or encountered) failures at each individual IO and
  synchronization point.
  - With multiple concurrent actors this may be achieved trhough 'lock-step' execution: with for example 2 related
    actors running concurrently which encounter a shared point of synchronization, run a test twice, once with the first
    actor running first, and once with the second actor running first.
- Do **not** use 'sleep' to simulate lock-step execution, timeouts, or other test conditions. Tests should strive to
  deterministically complete as quickly as possible via explicit synchronization.


### Runtime

- Unless forced to through interaction with external code, do not use environment variables for anything. Configuration
  should be injected, usually as keyword-only class constructor arguments, and usually in the form of dataclasses or
  `ta.NewType`s.
- Outside of test code, *NEVER* use `__file__` - never assume python code is running in `.py` files on a filesystem. (In
  general, do not even assume to have a readable filesystem). Write code compatible with zipfile python dists and
  pyoxidizer in which there is no `__file__`. Access resources via `lang.get_package_resources` /
  `lang.get_relative_resources`.
- In general, with very rare exception, 'everything (that does IO) needs a timeout', but the default may be large enough
  to never be realistically hit in practice (think 5m for interactive work, 1h for background work).
  - By default all pytests already run with a standard timeout.


### C Extensions

- C extensions use C11 and C++ extensions use C++20.
- In general prefer to write native extensions in C++.
- Use the C++ standard library liberally, but not 'excessively' lol. Write more 'C-style' code when interfacing with
  CPython.
- C/C++ extensions should have `// @omlish-cext` as their first line, and will thereafter be automatically built and
  packaged by existing codebase machinery.
- C/C++ extensions should be kept to a single, self-contained source file - do write new header files.
- C++ source files use the `.cc` extension, and C++ header files use the `.hh` extension.
- Native extensions *must* use PEP-489 style multi-phase extension initialization (`PyModuleDef_Init`).
- Modules should mark themselves `Py_MOD_GIL_NOT_USED` and `Py_MOD_MULTIPLE_INTERPRETERS_SUPPORTED` as applicable.
  Modules should strive to be written to support both if at all possible.
- See `omdev/cexts/_boilerplate.cc` for a simple C++ extension template.
