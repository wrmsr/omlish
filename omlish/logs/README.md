# Overview

A structured logging framework providing both sync and async loggers with stdlib compatibility, typed logging support,
and flexible output formatting. Designed as a modernized alternative to Python's stdlib `logging` module.

# Core Concepts

- **Logger** / **AsyncLogger** - Abstract base classes for sync and async logging. Provide the standard
  `debug()`/`info()`/`warning()`/`error()`/`critical()` interface.
- **LoggingContext** - Captures logging metadata (level, timestamp, stack info, exception info) at call time.
- **LogLevel** - Integer-based log levels compatible with stdlib logging (DEBUG=10, INFO=20, etc).
- **LoggingContextInfos** - Structured metadata attached to log events (level, timestamp, stack, exception).

# Key Features

- **Sync and async** - `Logger` for synchronous code, `AsyncLogger` for async contexts. Both share the same interface.
- **Stdlib compatibility** - `StdLogger` wraps stdlib `logging.Logger` instances, enabling gradual migration.
- **Typed logging** - Type-safe structured logging via `typed` subpackage with compile-time field validation.
- **Bisync logging** - `BisyncLogger` provides a single logger that works in both sync and async contexts.
- **List logging** - `ListLogger` captures log records to a list for testing and inspection.
- **Context capture** - Automatically captures caller location, timestamp, and exception info at log call sites.
- **JSON output** - `JsonFormatter` outputs structured JSON log records.
- **Flexible formatters** - Custom formatters for different output formats beyond stdlib's limited options.
- **Level filtering** - Fine-grained control over log levels per logger.
- **Module-level loggers** - `ModuleLogger` and `get_current_module_logger()` for automatic module-scoped logging.
- **Warning integration** - Capture Python warnings as log messages via `warnings` module integration.

# Notable Modules

- **[base](https://github.com/wrmsr/omlish/blob/master/omlish/logs/base.py)** - Core logger abstractions: `Logger`,
  `AsyncLogger`, `AnyLogger`, `NopLogger`.
- **[std](https://github.com/wrmsr/omlish/blob/master/omlish/logs/std)** - Stdlib logging integration:
  - **[loggers](https://github.com/wrmsr/omlish/blob/master/omlish/logs/std/loggers.py)** - `StdLogger` wraps stdlib
    `logging.Logger`.
  - **[handlers](https://github.com/wrmsr/omlish/blob/master/omlish/logs/std/handlers.py)** - Custom handlers for
    stdlib logging.
  - **[formatters](https://github.com/wrmsr/omlish/blob/master/omlish/logs/std/formatters.py)** - Custom formatters
    including `JsonFormatter`.
  - **[json](https://github.com/wrmsr/omlish/blob/master/omlish/logs/std/json.py)** - JSON log record formatting.
  - **[standard](https://github.com/wrmsr/omlish/blob/master/omlish/logs/std/standard.py)** - Standard logging
    configuration helpers.
- **[typed](https://github.com/wrmsr/omlish/blob/master/omlish/logs/typed)** - Type-safe structured logging:
  - **[types](https://github.com/wrmsr/omlish/blob/master/omlish/logs/typed/types.py)** - `TypedLoggerValue`,
    `TypedLoggerField` for typed field definitions.
  - **[values](https://github.com/wrmsr/omlish/blob/master/omlish/logs/typed/values.py)** - Value types for structured
    log fields.
  - **[bindings](https://github.com/wrmsr/omlish/blob/master/omlish/logs/typed/bindings.py)** - Binding structured
    values to loggers.
  - **[contexts](https://github.com/wrmsr/omlish/blob/master/omlish/logs/typed/contexts.py)** - Context management for
    typed logging.
- **[asyncs](https://github.com/wrmsr/omlish/blob/master/omlish/logs/asyncs.py)** - Async logger implementations.
- **[bisync](https://github.com/wrmsr/omlish/blob/master/omlish/logs/bisync.py)** - `BisyncLogger` for dual sync/async
  contexts.
- **[lists](https://github.com/wrmsr/omlish/blob/master/omlish/logs/lists.py)** - `ListLogger` captures log records to
  a list.
- **[modules](https://github.com/wrmsr/omlish/blob/master/omlish/logs/modules.py)** - Module-scoped logger utilities.
- **[levels](https://github.com/wrmsr/omlish/blob/master/omlish/logs/levels.py)** - Log level constants and utilities.
- **[contexts](https://github.com/wrmsr/omlish/blob/master/omlish/logs/contexts.py)** - `CaptureLoggingContext` and
  related context types.
- **[formatters](https://github.com/wrmsr/omlish/blob/master/omlish/logs/formatters.py)** - Custom log formatters.

# Example Usage

```python
from omlish.logs import base

class MyLogger(base.Logger):
    def _log(self, ctx, msg, *args, **kwargs):
        # Custom logging implementation
        print(f"[{ctx.level}] {msg}")

log = MyLogger()
log.info("Hello, %s!", "world")
log.error("An error occurred", exc_info=True)
```

# Stdlib Integration

```python
import logging
from omlish.logs.std import loggers

# Wrap stdlib logger
std_log = logging.getLogger(__name__)
log = loggers.StdLogger(std_log)

# Use omlish logger interface
log.info("This uses stdlib logging under the hood")
```

# Lite Compatibility

Core logging abstractions in `base.py`, `contexts.py`, `levels.py` are marked `@omlish-lite` and compatible with Python
3.8+. The `std` subpackage provides stdlib integration for lite environments.
