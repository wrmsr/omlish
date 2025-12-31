# Overview

Framework for building and managing daemon processes. Provides abstractions for services, launchers, spawning
strategies, and lifecycle management. Used as the foundation for process supervisors and long-running background
services.

# Core Concepts

- **Service** - Abstract unit of work that can be started, stopped, and monitored.
- **Target** - What to run (function, name, exec).
- **TargetRunner** - How to run a target.
- **Spawning** - How to create the process (fork, multiprocessing, thread).
- **Spawner** - Executes a target using a specific spawning strategy.
- **Launcher** - High-level orchestrator for spawning and managing services.
- **Daemon** - Unix daemon process management (detach from terminal, pidfile, etc.).
- **Wait** - Conditions to wait for before considering a service started (e.g., port listening, file exists).
- **Waiter** - Executes wait conditions.

# Key Features

- **Multiple spawning strategies** - Fork, multiprocessing, thread, or in-process execution.
- **Service abstractions** - Define services declaratively with targets, wait conditions, and spawning strategies.
- **Wait conditions** - Ensure services are fully started before proceeding (port listening, file existence, custom
  functions).
- **Daemon process management** - Full Unix daemon support (double-fork, pidfile, setsid, etc.).
- **Configuration-driven** - Services can be defined via configuration objects.
- **Launcher framework** - High-level API for managing collections of services.

# Notable Modules

- **[daemon](https://github.com/wrmsr/omlish/blob/master/omlish/daemons/daemon.py)** - `Daemon` class for Unix daemon
  process management.
- **[services](https://github.com/wrmsr/omlish/blob/master/omlish/daemons/services.py)** - `Service`,
  `ServiceTarget`, `ServiceConfigTarget` abstractions.
- **[targets](https://github.com/wrmsr/omlish/blob/master/omlish/daemons/targets.py)** - `Target`, `FnTarget`,
  `NameTarget`, `ExecTarget` for defining what to run.
- **[spawning](https://github.com/wrmsr/omlish/blob/master/omlish/daemons/spawning.py)** - `Spawner`,
  `ForkSpawner`, `MultiprocessingSpawner`, `ThreadSpawner` for different spawning strategies.
- **[waiting](https://github.com/wrmsr/omlish/blob/master/omlish/daemons/waiting.py)** - `Wait`, `ConnectWait`,
  `FnWait` for startup conditions.
- **[launching](https://github.com/wrmsr/omlish/blob/master/omlish/daemons/launching.py)** - `Launcher` for
  orchestrating services.
- **[reparent](https://github.com/wrmsr/omlish/blob/master/omlish/daemons/reparent.py)** - Process reparenting
  utilities.

# Example Usage

```python
from omlish import daemons

# Define a simple function-based service
def my_service():
    while True:
        print("Service running")
        time.sleep(1)

service = daemons.Service(
    target=daemons.FnTarget(my_service),
    spawning=daemons.ForkSpawning(),
    wait=daemons.FnWait(lambda: True),  # Service is ready immediately
)

# Launch the service
launcher = daemons.Launcher()
launcher.spawn(service)

# Or create a full Unix daemon
daemon = daemons.Daemon(
    target=daemons.FnTarget(my_service),
    pidfile='/var/run/myservice.pid',
)
daemon.start()
```

# Design Philosophy

The daemons framework provides:
- **Separation of concerns** - What to run (target), how to run it (spawner), when it's ready (waiter) are independent.
- **Composability** - Mix and match targets, spawners, and waiters.
- **Configuration-driven** - Define services via config objects, not code.
- **Production-ready** - Handle pidfiles, logging, signal handling, etc.

This package is used as the foundation for `ominfra.supervisor`, a process supervisor similar to
[Supervisor](https://github.com/Supervisor/supervisor) but rebuilt with modern patterns.
