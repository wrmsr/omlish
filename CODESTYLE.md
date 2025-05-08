- Environment
  - Target cpython 3.12 - use the modern language and library features it includes.
    - \[**lite**\] The exception is 'lite' code, which targets python 3.8.
  - Code should run on modern macOS and Linux - Windows support is not necessary, but still prefer things like
    `os.path.join` to `'/'.join` where reasonable.

- Imports
  - **Always** use relative imports within a package. **Never** reference the name of the root package from within
    itself. For example, within the `omlish` package, it's `from . import lang`, not `from omlish import lang`. Within
    the `omlish` root package there should never be an import line containing the word `omlish` - and references to the
    root name should be avoided in general.
  - Use the following import aliases for the following modules if they are used:
    - `import dataclasses as dc`
    - `import typing as ta`
  - For standard and external libraries, strongly prefer to import a module or package, rather than importing specific
    items from it. So for example, use `import typing as ta; fn: ta.Callable ...` as opposed to
    `from typing import Callable; fn: Callable ...`, and `import dataclasses as dc; @dc.dataclass() ...` as opposed to
    `from dataclasses import dataclass; @dataclass() ...`.
  - Unless instructed or unavoidable, prefer to use only the standard library and the current existing codebase.
    - Notable exceptions include:
      - anyio - In general async code should write to anyio rather than asyncio (or trio) unless it is specifically
        being written for a particular backend.
      - pytest - Write tests in pytest-style, and assume it is available.
    - \[**lite**\] 'lite' code can have no external dependencies of any kind, and can only reference other 'lite' code.
      - Lite async code uses only asyncio, and only uses functionality available in python 3.8.
      - Lite tests are written with the unittest package.
  - Avoid `pathlib` - use `os.path` instead.

- Dataclasses
  - Do not use zero-argument `@dc.dataclass` as a decorator - always use `@dc.dataclass()` even if there are no
    arguments.
  - Prefer frozen dataclasses.

- Type Annotation
  - Type annotate wherever possible, even if it is simply `ta.Any`, but use the most specific annotation feasible.
  - Prefer to accept immutable, less-specific types - a function should likely use a `ta.Sequence[int]` parameter rather
    than a `list[int]`. Use `ta.AbstractSet` over `set` and `frozenset`, and use `ta.Mapping` over `dict`, accordingly. 
  - When returning values, prefer to use the full type if the caller 'owns' the value, and use a less-specific, usually
    immutable type when the caller does not. For example, a utility function filtering out odd numbers from a
    `ta.Iterable[int]` can return a new `list[int]`, but a getter property on a class exposing some internal set of
    integers should probably return a `ta.AbstractSet[int]` rather than a `set[int]`.
  - Don't avoid `ta.Generic` and type parameters where it makes sense, but usually annotating something as a superclass
    will suffice.
  - Use PEP-585 style annotations - use `list[int]` instead of `ta.List[int]`, and `int | None` instead of
    `ta.Optional[int]`.

- Classes
  - Ensure constructors call `super().__init__()`, even if they don't appear to inherit from anything at their
    definition.
  - Prefer to use dataclasses for even moderately complex usecases - if there are, say, more than a 2-element tuple, a
    dataclass should probably be used.
  - `ta.NamedTuple` still has usecases, such as replacing a function's return type from an anonymous tuple to a named
    one (to allow it to be destructured by callers as before), but in general almost always prefer dataclasses.
  - Don't be shy about creating new classes with methods to reduce the number of arguments being passed around to
    related functions, even if the class is considered implementation detail and not part of any public api.
  - For any necessary global state, consider encapsulating it in a class, even if it's only a singleton.
  - Prefer stateless classes, taking dependencies as constructor arguments and not mutating them once set, and passing
    around and returning dataclasses for intermediate data.
  - While not necessarily the case, write code as if it were to be injected by a guice-style dependency injector.
  - Prefer relatively fine-grained dependency decomposition.
  - For situations in which different behaviors are necessary, prefer to define an `abc.ABC` interface with
    `@abc.abstractmethod` members, and write multiple implementations of them as warranted. Prefer to refer to the
    interface in type annotations unless it must specifically refer to a given implementation.
  - When naming interface classes, the interface should be the 'bare' name, and implementations should have prefixes and
    suffixes. For example, a user service interface would be `UserService`, with a `DbUserService` or `DictUserService`
    subclass, or even a `UserServiceImpl` subclass if there is only one sensible initial implementation but it still
    justifies being abstracted.

- Modules
  - Avoid global state in general. Constants are however fine.
  - Avoid code execution in module bodies. If necessary, add a `def _main() -> None:` and conditional
    `if __name__ == '__main__':` call to it.

- Errors
  - Never use the `assert` statement anywhere but test code - rather, check a condition and raise an `Exception` if
    necessary.
    - Prefer to use the 'check' system (`from omlish import check`, or `from omlish.lite.check import check` for lite
      code) where `assert` would otherwise be used.
  - Outside of `TypeError`, `ValueError`, and `RuntimeError`, prefer to create custom subclasses of `Exception` for more
    specific errors. Use inheritance where beneficial to communicate subtypes of errors.
    - `KeyError` should however not be raised except in the specific and rare case of implementing a `ta.Mapping` or
      direct equivalent. For example, a `UserService` `get_user` method should raise a `UserNotFoundError`, not
      `KeyError`, when a given user is not found.

- Comments
  - Avoid unnecessary and frivolous comments. Most semantic meaning should be able to be inferred from package / module
    / type / method / function / parameter names and annotations. For example a function like
    `def add_two_floats(x: float, y: float) -> float:` does not need a docstring or comments.
  - Reserve inline comments for 'surprising' or dangerous things, such as invariants which must be maintained. A comment
    like `self._ensure_user_exists()  # ensure user exists` is worthless, but a comment like
    `self._ensure_user_exists()  # safe because we already hold the user lock` is valuable.

- Tests
  - As above, write tests in pytest-style.
  - Use raw assertions liberally in tests, and use pytest utilities like `pytest.raises`.
  - Use fixtures and other advanced pytest features sparingly. Prefer to simply instantiate test data rather than wrap
    it in a fixture.
  - Avoid mocks - prefer to structure code such that a 'simple' but still functioning implementation of an interface can
    be used where a mock would otherwise. For example, for a some `UserService` interface with an `add_user` method, for
    which a `RemoteUserService` would usually make a remote service call, prefer to implement a `DictUserService` class
    with an `add_user` method such that it actually stores the added user in a dictionary on the instance.
