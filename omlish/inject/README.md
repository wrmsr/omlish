# Overview

A [Guice](https://github.com/google/guice)-style dependency injection framework. Supports sync, async, and maysync (dual
sync/async) injection modes with full type safety and advanced binding capabilities.

# Core Concepts

- **Keys** - Type-tagged identifiers for bindings. A `Key[UserService]` uniquely identifies a dependency, optionally
  with additional tag metadata.
- **Bindings** - Declarations mapping keys to providers. Can be simple constants, factories, constructors, or links to
  other keys.
- **Providers** - Factories for creating instances. Includes `ConstProvider`, `FnProvider`, `AsyncFnProvider`,
  `CtorProvider`, and `LinkProvider`.
- **Injectors** - Runtime containers that resolve and instantiate dependencies. Three modes: `Injector` (sync),
  `AsyncInjector` (async), and `MaysyncInjector` (dual mode).
- **Scopes** - Lifecycle managers for instances. Built-in scopes include `Singleton`, `ThreadScope`, and `SeededScope`.
- **Elements** - Composable configuration units assembled into injectors. Includes bindings, scope definitions, private
  modules, and provision listeners.

# Key Features

- **Type-safe injection** - Generic `Key[T]` ensures compile-time type correctness when resolving dependencies.
- **Multiple injection modes** - Sync, async, and maysync injectors support different execution contexts without code
  duplication.
- **Constructor injection** - Automatic dependency resolution via type annotations on `__init__` parameters.
- **Private modules** - Encapsulate implementation details while exposing only public bindings via `expose()`.
- **Multibindings** - `SetBinder` and `MapBinder` for collecting multiple bindings into sets or maps.
- **Scoped instances** - Control instance lifecycle with scopes. `SeededScope` enables request-scoped dependencies.
- **Lifecycle integration** - `create_managed_injector()` integrates with the `lifecycles` package for startup/shutdown.
- **Provision listeners** - Hook into dependency creation for cross-cutting concerns like logging or validation.
- **Override support** - Replace bindings in child injectors without modifying parent configuration.
- **Assisted injection** - Mix injected and user-provided constructor parameters.
- **Late binding** - `Late[T]` and `AsyncLate[T]` for circular dependency resolution.

# Notable Modules

- **[helpers](https://github.com/wrmsr/omlish/blob/master/omlish/inject/helpers)** - Utilities for common injection
  patterns:
  - **[late](https://github.com/wrmsr/omlish/blob/master/omlish/inject/helpers/late.py)** - `Late[T]` and
    `AsyncLate[T]` for breaking circular dependencies.
  - **[managed](https://github.com/wrmsr/omlish/blob/master/omlish/inject/helpers/managed.py)** - Integration with
    lifecycle management for async resource handling.
  - **[multis](https://github.com/wrmsr/omlish/blob/master/omlish/inject/helpers/multis.py)** - Helpers for set and map
    multibindings.
  - **[wrappers](https://github.com/wrmsr/omlish/blob/master/omlish/inject/helpers/wrappers.py)** - Wrapper pattern
    support for decorating injected instances.
- **[scopes](https://github.com/wrmsr/omlish/blob/master/omlish/inject/scopes.py)** - Scope implementations including
  `Singleton`, `ThreadScope`, and `SeededScope`.
- **[lite](https://github.com/wrmsr/omlish/blob/master/omlish/inject/lite.py)** - See `omlish.lite.inject` for the
  lightweight 3.8+ compatible injector.

# Example Usage

```python
from omlish import inject as inj

class UserService:
    pass

class AuthService:
    def __init__(self, users: UserService) -> None:
        self.users = users

# Create injector with bindings
injector = inj.create_injector(inj.as_elements(
    inj.bind(UserService),
    inj.bind(AuthService),
))

# Resolve dependencies
auth = injector[AuthService]
```

# Comparison to Lite Injector

The standard injector offers significantly more features than `omlish.lite.inject`:
- Async and maysync support
- Scope implementations beyond singleton
- Private modules and overrides
- Multibindings
- Provision listeners
- Lifecycle integration
- Extensive reflection and metadata

Use the lite injector when targeting Python 3.8+ or when a minimal footprint is required.
