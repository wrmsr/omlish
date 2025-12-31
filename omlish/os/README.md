# Overview

Operating system utilities and low-level OS interactions. Includes file locking, signal handling, process management,
atomic file operations, and Linux-specific features.

# Key Features

- **Atomic operations** - Atomic file writes and renames.
- **File locking** - Cross-platform file locking with fcntl support.
- **Pidfiles** - Process ID file management for daemons.
- **Signal handling** - Enhanced signal handling utilities.
- **Fork hooks** - Register callbacks to run before/after fork.
- **Environment variables** - Environment manipulation utilities.
- **File modes** - File permission and mode utilities.
- **Journald integration** - systemd journal logging support.
- **Linux-specific** - Linux kernel interfaces and features.
- **Death pacts** - Process monitoring and auto-termination when parent dies.

# Notable Modules

- **[atomics](https://github.com/wrmsr/omlish/blob/master/omlish/os/atomics.py)** - Atomic file operations (write,
  rename, replace).
- **[fcntl](https://github.com/wrmsr/omlish/blob/master/omlish/os/fcntl.py)** - File control and locking via fcntl.
- **[pidfiles](https://github.com/wrmsr/omlish/blob/master/omlish/os/pidfiles)** - PID file creation and management for
  daemon processes.
- **[signals](https://github.com/wrmsr/omlish/blob/master/omlish/os/signals.py)** - Signal handling utilities including
  context managers.
- **[forkhooks](https://github.com/wrmsr/omlish/blob/master/omlish/os/forkhooks.py)** - Register pre-fork and
  post-fork hooks.
- **[environ](https://github.com/wrmsr/omlish/blob/master/omlish/os/environ.py)** - Environment variable utilities.
- **[filemodes](https://github.com/wrmsr/omlish/blob/master/omlish/os/filemodes.py)** - File permission/mode
  manipulation.
- **[journald](https://github.com/wrmsr/omlish/blob/master/omlish/os/journald.py)** - systemd journal integration.
- **[linux](https://github.com/wrmsr/omlish/blob/master/omlish/os/linux.py)** - Linux kernel features and interfaces.
- **[deathpacts](https://github.com/wrmsr/omlish/blob/master/omlish/os/deathpacts)** - Process death pact system for
  monitoring parent process.

# Example Usage

```python
from omlish.os import atomics

# Atomic file write (write to temp, then rename)
atomics.atomic_write('/path/to/file', b'content')

# File locking
from omlish.os import fcntl
with fcntl.lock_file('/path/to/lockfile'):
    # Critical section - only one process can enter
    pass

# PID file management
from omlish.os import pidfiles
with pidfiles.pidfile_context('/var/run/myapp.pid'):
    # Run daemon - pidfile created and cleaned up automatically
    run_daemon()

# Signal handling
from omlish.os import signals
with signals.signal_context({signal.SIGTERM: handle_sigterm}):
    # Custom signal handler installed
    pass
```

# Design Philosophy

OS utilities should:
- **Be cross-platform where possible** - Abstract platform differences when feasible.
- **Be explicit about platform requirements** - Linux-specific features are clearly marked.
- **Handle edge cases** - Atomic operations, race conditions, signal handling edge cases.
- **Be production-ready** - Suitable for daemon processes and production systems.

These utilities are particularly important for:
- Daemon processes (`omlish.daemons`)
- Process supervisors (`ominfra.supervisor`)
- Long-running services
- Multi-process applications

# Linux-Specific Features

Several modules are Linux-specific:
- `journald` - systemd journal support
- `linux` - Linux kernel interfaces
- Parts of `deathpacts` - Use Linux-specific process monitoring

When writing cross-platform code, check platform before using these features or provide fallbacks.
