# Overview

Terminal and console utilities for building CLI applications with colors, progress bars, VT100 sequences, and terminal
state management.

# Key Features

- **Color output** - ANSI color code generation and terminal coloring.
- **Progress bars** - Configurable progress indicators for long-running operations.
- **VT100 sequences** - VT100/ANSI escape sequence generation and parsing.
- **Terminal info** - Query terminal capabilities via terminfo.
- **Terminal state** - Track and manage terminal state (cursor position, colors, etc.).
- **Pager** - Display long output through a pager (like `less`).
- **Confirmation prompts** - Interactive yes/no prompts.
- **Alternative screen** - Use terminal's alternative screen buffer.

# Notable Modules

- **[coloring](https://github.com/wrmsr/omlish/blob/master/omlish/term/coloring.py)** - ANSI color output and
  formatting.
- **[progressbar](https://github.com/wrmsr/omlish/blob/master/omlish/term/progressbar.py)** - Progress bar
  implementation.
- **[vt100](https://github.com/wrmsr/omlish/blob/master/omlish/term/vt100)** - VT100/ANSI escape sequence handling.
- **[terminfo](https://github.com/wrmsr/omlish/blob/master/omlish/term/terminfo.py)** - Terminal capability database
  queries.
- **[termstate](https://github.com/wrmsr/omlish/blob/master/omlish/term/termstate.py)** - Terminal state tracking.
- **[codes](https://github.com/wrmsr/omlish/blob/master/omlish/term/codes.py)** - ANSI code constants and utilities.
- **[pager](https://github.com/wrmsr/omlish/blob/master/omlish/term/pager.py)** - Pager integration for long output.
- **[confirm](https://github.com/wrmsr/omlish/blob/master/omlish/term/confirm.py)** - Interactive confirmation prompts.
- **[alt](https://github.com/wrmsr/omlish/blob/master/omlish/term/alt.py)** - Alternative screen buffer support.

# Example Usage

```python
from omlish.term import coloring

# Colored output
print(coloring.red("Error!"))
print(coloring.green("Success!"))
print(coloring.bold(coloring.blue("Important")))

# Progress bar
from omlish.term import progressbar
for i in progressbar.progress(range(100)):
    # Do work
    time.sleep(0.01)

# Confirmation prompt
from omlish.term import confirm
if confirm.confirm("Continue?"):
    print("Continuing...")
```

# Design Philosophy

Terminal utilities should:
- **Handle terminal variations** - Work across different terminal emulators and capabilities.
- **Be optional** - Gracefully degrade when terminal features aren't available (e.g., no color support).
- **Be lightweight** - Don't pull in heavy UI frameworks for simple CLI needs.
- **Be composable** - Small utilities that can be combined.

These utilities are particularly useful for:
- CLI applications (`omdev.cli`)
- Developer tools
- Interactive scripts
- Status displays and monitoring

# Terminal Compatibility

Code checks terminal capabilities before using features like:
- Colors (via `isatty()` and `TERM` environment variable)
- Cursor movement (via terminfo)
- Alternative screen (terminal support detection)

This ensures output works correctly when:
- Redirected to files
- Piped to other commands
- Running in non-interactive environments
