# Overview

Diagnostics and debugging utilities for introspection, profiling, remote debugging, and runtime analysis. Integrates
with PyCharm, VSCode debuggers, and provides process-level diagnostic tools.

# Key Features

- **Remote debugging** - Attach PyCharm or VSCode debuggers to running processes.
- **Process introspection** - Read `/proc` filesystem for process stats and info.
- **Thread inspection** - Dump thread stacks and analyze thread states.
- **AST tools** - Utilities for inspecting and manipulating Python ASTs.
- **Timing utilities** - High-precision timers for profiling.
- **REPL server** - Embed a remote REPL in running processes for live debugging.
- **Debug commands** - CLI commands for common debugging tasks.

# Notable Modules

- **[pycharm](https://github.com/wrmsr/omlish/blob/master/omlish/diag/pycharm.py)** - PyCharm remote debugger
  integration (`pydevd`).
- **[pydevd](https://github.com/wrmsr/omlish/blob/master/omlish/diag/pydevd.py)** - Low-level pydevd debugger
  utilities.
- **[debug](https://github.com/wrmsr/omlish/blob/master/omlish/diag/debug.py)** - General debugging utilities and
  helpers.
- **[threads](https://github.com/wrmsr/omlish/blob/master/omlish/diag/threads.py)** - Thread inspection and stack
  dumping.
- **[procfs](https://github.com/wrmsr/omlish/blob/master/omlish/diag/procfs.py)** - `/proc` filesystem parsing for
  Linux process info.
- **[procstats](https://github.com/wrmsr/omlish/blob/master/omlish/diag/procstats.py)** - Process statistics and
  monitoring.
- **[asts](https://github.com/wrmsr/omlish/blob/master/omlish/diag/asts.py)** - AST introspection and manipulation.
- **[timers](https://github.com/wrmsr/omlish/blob/master/omlish/diag/timers.py)** - High-precision timing utilities.
- **[replserver](https://github.com/wrmsr/omlish/blob/master/omlish/diag/replserver)** - Remote REPL server for live
  debugging.
- **[cmds](https://github.com/wrmsr/omlish/blob/master/omlish/diag/cmds)** - CLI commands for debugging tasks.

# Example Usage

```python
from omlish.diag import pycharm

# Attach PyCharm debugger to running process
pycharm.setup_remote_debugging(host='localhost', port=5678)

# Dump all thread stacks
from omlish.diag import threads
threads.dump_all_stacks()

# Get process memory info from /proc
from omlish.diag import procfs
info = procfs.read_proc_status()
print(f"RSS: {info['VmRSS']}")
```

# Remote Debugging

PyCharm remote debugging enables attaching a debugger to a running Python process:

1. In PyCharm, create a "Python Debug Server" run configuration.
2. Start the debug server.
3. In your code, call `pycharm.setup_remote_debugging(port=5678)`.
4. PyCharm will attach and breakpoints will work.

This is invaluable for debugging production issues, long-running processes, or code running in containers.

# Design Philosophy

Diagnostic tools should be:
- **Non-invasive** - Minimal impact on the running process.
- **Production-safe** - Safe to include in production code, activated when needed.
- **Framework-agnostic** - Work with any Python code, not tied to specific frameworks.
- **Cross-platform** where possible - Though some features (like `/proc` parsing) are Linux-specific.

See the `bootstrap` package for integrating diagnostic tools into application startup.
