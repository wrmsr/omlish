# omlish.inject

A Guice-inspired dependency injection system for Python with first-class async support and a focus on type safety.

## Overview

`omlish.inject` provides constructor-based dependency injection with explicit, declarative configuration. Like Guice, it
emphasizes immutability, composition over inheritance, and pure constructor injection. Unlike Guice, it embraces
Python's native type system, provides native async/await support, and uses a functional elements-based configuration
model.

The system is built around three core concepts:
- **Keys** identify dependencies by type and optional tag
- **Bindings** associate keys with providers
- **Injectors** resolve and provide instances

## Core API

### Keys

A `Key` identifies a dependency by its type and an optional tag for disambiguation:

```python
from omlish import inject as inj

# Simple key by type
int_key = inj.Key(int)

# Tagged key for multiple bindings of the same type
db_conn_key = inj.Key(DbConnection, tag='primary')
cache_conn_key = inj.Key(DbConnection, tag='cache')

# Convert any type to a key
key = inj.as_key(MyService)
```

### Bindings

Bindings connect keys to providers. The `bind()` function provides a concise API for most use cases:

```python
# Bind a constant
inj.bind(420)

# Bind a type to its constructor
inj.bind(UserService)

# Bind to a factory function
def make_conn(cfg: Config) -> Connection:
    return create_connection(cfg)
inj.bind(make_conn)

# Bind to another key (linking)
inj.bind(Service, to_key=ServiceImpl)

# Tagged binding
inj.bind(420, tag='port')

# Scoped binding
inj.bind(Database, singleton=True)
```

### Providers

Providers define how to construct instances. The system includes several built-in provider types:

- `ConstProvider` - returns a constant value
- `CtorProvider` - calls a constructor
- `FnProvider` - calls a function
- `AsyncFnProvider` - calls an async function
- `LinkProvider` - delegates to another key

Providers are typically created implicitly through `bind()`, but can be used directly for advanced cases.

### Injectors

Injectors resolve dependencies and provide instances:

```python
# Create an injector
injector = inj.create_injector(
    inj.bind(420),
    inj.bind(str, to_fn=inj.KwargsTarget.of(lambda i: f'Port: {i}', i=int)),
)

# Provide instances
port = injector[int]  # 420
msg = injector.provide(str)  # 'Port: 420'

# Check if a key is bound
maybe_val = injector.try_provide(SomeService)
```

For async code, use `AsyncInjector`:

```python
async_injector = await inj.create_async_injector(
    inj.bind(async_factory),
)

service = await async_injector[MyService]
```

### Elements

`Elements` are the building blocks of injector configuration. Most binding functions return `Element` or `Elements`:

```python
# Combine multiple elements
config = inj.as_elements(
    inj.bind(DatabaseConfig(host='localhost')),
    inj.bind(Database, singleton=True),
    inj.bind(UserRepository),
)

# Elements can be reused
injector1 = inj.create_injector(config)
injector2 = inj.create_injector(config)

# Collect elements once for efficiency
collected = inj.collect_elements(config)
injector3 = inj.create_injector(collected)
```

### Scopes

Scopes control instance lifecycle:

```python
# Singleton scope - one instance per injector
inj.bind(Database, singleton=True)
inj.bind(Cache, in_='singleton')

# Thread scope - one instance per thread
inj.bind(RequestContext, in_='thread')

# Seeded scope - manually seeded instances
request_scope = inj.SeededScope('request')
inj.bind_scope(request_scope)
inj.bind(UserId, in_=request_scope)
inj.bind_scope_seed(RequestContext, request_scope)

with inj.enter_seeded_scope(injector, request_scope, {
    inj.as_key(RequestContext): ctx,
}):
    user_id = injector[UserId]
```

## Differences from Guice

While inspired by Guice, `omlish.inject` differs in several key ways:

### Type System
- Uses Python's native `typing` module instead of Java generics
- No annotation-based injection (no `@Inject` decorator)
- Type annotations on constructors/functions drive automatic injection

### Async Support
- Native `AsyncInjector` for async dependency graphs
- `AsyncFnProvider` for async factories
- Async-aware scopes and lifecycle management

### Configuration Model
- `Elements`-based functional composition instead of module classes
- Functions return `Elements` rather than imperative `configure()` methods
- More flexible composition and reuse

### Dependency Resolution
- Automatic kwarg inspection via `KwargsTarget`
- Supports optional dependencies (parameters with defaults)
- Explicit async/sync separation

### Python Idioms
- `__getitem__` syntax for common case: `injector[MyService]`
- Context managers for lifecycle and scoped execution
- Dataclasses as natural config objects

## Common Idioms

### Hierarchical Package-Level Modules

Organize bindings into composable, package-level functions that mirror your application structure:

```python
# app/services/inject.py
def bind_services(cfg: ServicesConfig) -> inj.Elements:
    return inj.as_elements(
        inj.bind(UserService, singleton=True),
        inj.bind(AuthService, singleton=True),
    )

# app/database/inject.py
def bind_database(cfg: DatabaseConfig) -> inj.Elements:
    return inj.as_elements(
        inj.bind(cfg),
        inj.bind(Database, singleton=True),
    )

# app/inject.py
def bind_app(cfg: AppConfig) -> inj.Elements:
    return inj.as_elements(
        bind_database(cfg.database),
        bind_services(cfg.services),
    )
```

This pattern enables:
- Clear separation of concerns
- Easy testing of subsystems
- Configuration composition
- Lazy imports (using `lang.auto_proxy_import`)

### Multi-Bindings

Collect multiple bindings into sets or maps:

```python
# Set bindings
inj.set_binder[Plugin]().bind(
    inj.Key(Plugin, tag='auth'),
    inj.Key(Plugin, tag='logging'),
)
plugins = injector[ta.AbstractSet[Plugin]]

# Map bindings
inj.map_binder[str, Handler]().bind('GET', GetHandler)
inj.map_binder[str, Handler]().bind('POST', PostHandler)
handlers = injector[ta.Mapping[str, Handler]]

# Helper for const entries
inj.bind_set_entry_const(ta.AbstractSet[str], 'value1')
inj.bind_map_entry_const(ta.Mapping[str, int], 'key', 42)
```

### Private Modules

Encapsulate internal bindings while exposing only specific keys:

```python
inj.private(
    inj.bind('jdbc:postgresql://internal-db'),
    inj.bind(DbConnection, singleton=True),
    inj.bind(UserRepository, expose=True),
)
```

Only `UserRepository` is visible to the parent injector; the connection string and `DbConnection` remain private.

### Overrides

Replace bindings for testing or configuration:

```python
production = inj.bind(Database, to_ctor=PostgresDatabase)

testing = inj.override(
    production,
    inj.bind(Database, to_ctor=InMemoryDatabase),
)
```

### Late Bindings

Break circular dependencies by injecting factories:

```python
class ServiceA:
    def __init__(self, b: 'ServiceB') -> None: ...

class ServiceB:
    def __init__(self, c: 'ServiceC') -> None: ...

class ServiceC:
    def __init__(self, a: inj.Late[ServiceA]) -> None:
        self.get_a = a  # Callable that returns ServiceA

inj.create_injector(
    inj.bind(ServiceA, singleton=True),
    inj.bind(ServiceB, singleton=True),
    inj.bind(ServiceC, singleton=True),
    inj.bind_late(ServiceA),
)
```

### Managed Providers

Integrate with context managers for lifecycle management:

```python
# Automatic context manager handling
with inj.create_managed_injector(
    inj.bind(
        Database,
        singleton=True,
        to_fn=inj.make_managed_provider(Database),
    ),
) as injector:
    db = injector[Database]
    # Database.__enter__ called automatically
# Database.__exit__ called on scope exit

# Wrap with custom lifecycle
inj.bind(
    Resource,
    to_fn=inj.make_managed_provider(
        create_resource,
        contextlib.closing,
    ),
)
```

### KwargsTarget

Explicitly control function parameter injection:

```python
# Manual kwarg specification
target = inj.KwargsTarget.of(
    my_function,
    db=DatabaseKey,
    cache=(CacheKey, True),  # has_default=True
)
inj.bind(MyService, to_fn=target)

# Decorator syntax
@inj.target(db=Database, cache=Cache)
def create_service(db, cache):
    return Service(db, cache)

inj.bind(Service, to_fn=create_service)
```

### Wrapper Binder Helper

Build decorator chains of providers:

```python
stack = inj.wrapper_binder_helper(Service)

# Each layer wraps the previous
stack.push_bind(to_ctor=LoggingServiceWrapper)
stack.push_bind(to_ctor=RetryServiceWrapper)
stack.push_bind(to_ctor=MetricsServiceWrapper)

# Final binding gets the fully-wrapped stack
inj.bind(Service, to_key=stack.top)
```

### Items Binder Helper

Collect and aggregate items across multiple bindings:

```python
Plugins = ta.NewType('Plugins', ta.Sequence[Plugin])
helper = inj.items_binder_helper[Plugin](Plugins)

inj.as_elements(
    helper.bind_items_provider(),
    helper.bind_item_consts(plugin1, plugin2),
    helper.bind_item(to_ctor=DynamicPlugin),
)

plugins = injector[Plugins]  # All collected plugins
```

### Eager Bindings

Force instantiation at injector creation:

```python
# Start background tasks immediately
inj.bind(BackgroundWorker, singleton=True, eager=True)

# Control initialization order with priority
inj.bind(Database, singleton=True, eager=1)
inj.bind(Cache, singleton=True, eager=2)
inj.bind(Service, singleton=True, eager=3)
```

### Provision Listeners

Intercept instance provision for logging, metrics, or instrumentation:

```python
async def log_provisions(
    injector: inj.AsyncInjector,
    key: inj.Key,
    binding: inj.Binding | None,
    provide: ta.Callable[[], ta.Awaitable[ta.Any]],
) -> ta.Any:
    start = time.time()
    result = await provide()
    duration = time.time() - start
    log.info(f'Provided {key} in {duration:.3f}s')
    return result

inj.bind_provision_listener(log_provisions)
```

## Error Handling

The system provides clear error types for common issues:

- `UnboundKeyError` - no binding exists for a requested key
- `ConflictingKeyError` - multiple conflicting bindings for the same key
- `CyclicDependencyError` - circular dependency detected
- `ScopeError` - scope-related errors (not open, already open)

## Advanced Topics

### MaysyncInjector

For code that supports both sync and async execution:

```python
maysync_injector = inj.create_maysync_injector(...)
# Can be used in both sync and async contexts
```

### Custom Scopes

Define application-specific scopes by implementing the `Scope` interface and registering with `bind_scope()`.

### Origins

Track binding sources for debugging with the `HasOrigins` interface and `Origin` metadata.

### Inspection

Use `inj.tag()` and `inj.build_kwargs_target()` for runtime parameter inspection and custom injection logic.
