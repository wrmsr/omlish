# Overview

Process management utilities for spawning, monitoring, and controlling subprocesses. Provides sync, async, and maysync
APIs with enhanced error handling, output capture, and process lifecycle management.

# Key Features

- **Sync/async/maysync** - Unified subprocess APIs across sync, async, and dual-mode contexts.
- **Enhanced error handling** - Better exception messages with command details and output.
- **Output capture** - Flexible stdout/stderr capture and streaming.
- **Process wrapping** - Convenient wrappers around stdlib `subprocess` with better defaults.
- **Interactive editors** - Launch interactive editors (`EDITOR` environment variable) for user input.
- **Command building** - Fluent APIs for building subprocess commands.

# Notable Modules

- **[base](https://github.com/wrmsr/omlish/blob/master/omlish/subprocesses/base.py)** - Core subprocess abstractions
  and types.
- **[sync](https://github.com/wrmsr/omlish/blob/master/omlish/subprocesses/sync.py)** - Synchronous subprocess
  execution.
- **[asyncs](https://github.com/wrmsr/omlish/blob/master/omlish/subprocesses/asyncs.py)** - Asynchronous subprocess
  execution.
- **[maysync](https://github.com/wrmsr/omlish/blob/master/omlish/subprocesses/maysync.py)** - Dual sync/async
  subprocess execution.
- **[run](https://github.com/wrmsr/omlish/blob/master/omlish/subprocesses/run.py)** - High-level subprocess running
  utilities.
- **[editor](https://github.com/wrmsr/omlish/blob/master/omlish/subprocesses/editor.py)** - Interactive editor
  launching for user input.
- **[wrap](https://github.com/wrmsr/omlish/blob/master/omlish/subprocesses/wrap.py)** - Process wrapper utilities.
- **[utils](https://github.com/wrmsr/omlish/blob/master/omlish/subprocesses/utils.py)** - Subprocess utility functions.

# Example Usage

```python
from omlish.subprocesses import run

# Simple command execution
result = run.run_command(['ls', '-la'])
print(result.stdout)

# With error handling
result = run.run_command(['false'], check=True)  # Raises on non-zero exit

# Async execution
async def run_async():
    result = await run.run_command_async(['ls', '-la'])
    print(result.stdout)

# Interactive editor
from omlish.subprocesses import editor
text = editor.edit_text("Initial content")  # Opens $EDITOR, returns edited text
```

# Design Philosophy

Subprocess utilities should:
- **Provide better defaults** than stdlib `subprocess` (e.g., capture output by default, better error messages).
- **Support multiple execution modes** - sync, async, and maysync for maximum flexibility.
- **Be testable** - Make it easy to mock subprocess calls in tests.
- **Handle errors well** - Include command details and output in exceptions.

This package wraps stdlib `subprocess` with higher-level APIs that are more convenient for common use cases while
maintaining full access to low-level features when needed.
