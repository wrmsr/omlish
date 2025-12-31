# Overview

Centralized, configurable process initialization for setting up resource limits, profiling, remote debugging, logging,
environment variables, and other startup concerns. Provides an all-in-one context manager and CLI for bootstrapping
Python applications.

# Key Features

- **Resource limits** - Set rlimits (file descriptors, memory, CPU time, etc.) at startup.
- **Profiling** - Enable CPU profiling, memory profiling, or tracing.
- **Remote debugging** - Attach PyCharm or other debuggers at startup.
- **Log configuration** - Configure logging levels, handlers, and formatters.
- **Environment setup** - Set environment variables and system configuration.
- **Diagnostic tools** - Enable diagnostic features (thread dumps, signal handlers, etc.).
- **Context manager API** - Use as a context manager for scoped setup/teardown.
- **CLI integration** - Command-line interface for bootstrapping applications.

# Core Concepts

- **Bootstrap** - Central configuration object containing all startup settings.
- **Bootstrap context** - Context manager that applies bootstrap configuration and cleans up on exit.
- **Bootstrap CLI** - Command-line wrapper that bootstraps then runs a target application.

# Notable Modules

- **[base](https://github.com/wrmsr/omlish/blob/master/omlish/bootstrap/base.py)** - Core bootstrap abstractions and
  configuration.
- **[main](https://github.com/wrmsr/omlish/blob/master/omlish/bootstrap/main.py)** - Bootstrap CLI implementation.
- **[sys](https://github.com/wrmsr/omlish/blob/master/omlish/bootstrap/sys.py)** - System-level bootstrap (resource
  limits, etc.).
- **[diag](https://github.com/wrmsr/omlish/blob/master/omlish/bootstrap/diag.py)** - Diagnostic bootstrap (profiling,
  debugging).
- **[harness](https://github.com/wrmsr/omlish/blob/master/omlish/bootstrap/harness.py)** - Test harness integration.

# Example Usage

```python
from omlish import bootstrap

# Create bootstrap configuration
config = bootstrap.Bootstrap(
    resource_limits={'nofile': 10000},
    profiling={'cpu': True},
    remote_debug={'pycharm': {'port': 5678}},
    log_level='DEBUG',
)

# Use as context manager
with bootstrap.bootstrap_context(config):
    # Application runs with bootstrap configuration
    run_application()

# Or use the CLI
# python -m omlish.bootstrap --log-level=DEBUG --profile-cpu myapp.py
```

# Bootstrap via CLI

The bootstrap CLI allows configuring initialization via command-line flags:

```bash
# Set resource limits and enable profiling
python -m omlish.bootstrap \
  --rlimit-nofile=10000 \
  --profile-cpu \
  -- python myapp.py

# Enable remote debugging
python -m omlish.bootstrap \
  --remote-debug-pycharm=5678 \
  -- python myapp.py
```

# Design Philosophy

Bootstrap should:
- **Centralize initialization** - One place for all startup configuration, not scattered across codebase.
- **Be configurable** - Support both programmatic and CLI configuration.
- **Be composable** - Different bootstrap concerns are independent and can be mixed/matched.
- **Be production-ready** - Suitable for production deployments, not just development.

This package is particularly valuable for:
- Production deployments (resource limits, logging)
- Development (remote debugging, profiling)
- Testing (test harness integration)
- Process supervisors (standardized initialization)

Use bootstrap when you need consistent process initialization across development, testing, and production environments.
