main:

- !! dynamic process group updates lol
  - supervisord diff_to_active, add_process_group, do_update, etc
- supervisor (omcore) pidfile
- process pidfiles
- named instances
- nested instances
- log infra (self and forwarded from subprocesses)
  - rotating
- journald no longer default, but supported
- richer json http endpoints
  - POSTs
    - `POST /api/processes/{name}/start` - Start process
    - `POST /api/processes/{name}/stop` - Stop process
    - `POST /api/processes/{name}/signal` - Send signal
    - `GET /api/events?since=N` - Get events (see below)
- event listeners
  - subprocesses like og supd
  - streaming http endpoints (sse, longpoll)
- scheduler
- systemd? less urgent now
- serializable / diffable process cfg, process state
- prctl / pgrp killer failsafe
- maybe GroupName/ProcessName/Namespec NewTypes?

tests:

- more knobs
  - backoff_secs
- more logging (special json event stream)
  - `{"type": "ProcessStateEvent", "process": "worker", "from": "STARTING", "to": "RUNNING", "ts": 1234.56}`
  - `{"type": "ProcessLogEvent", "process": "worker", "channel": "stdout", "data": "...", "ts": 1234.57}`
- in-proc support?
  - `supervisor.step()`
  - injected 'fake' signal manager
- better sync than friggin sleeps
- more tests:
  - User/UID switching (requires root)
  - Resource limit testing (ulimit)
  - Log file rotation (once implemented)
  - Config reloading (once implemented)
  - num_procs expansion (once fully implemented)

reload:

- self-update - state handoff - fd's, subprocesses, timers, etc
- check script file id via (st_dev, st_ino):
```python
import errno
import os
import stat


def same_file_as_fd_by_opening(fd: int, path: str) -> bool:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)

    # Linux-only: O_PATH is ideal when available, because it opens a reference
    # to the path without requiring normal read access.
    flags = getattr(os, "O_PATH", flags) | getattr(os, "O_CLOEXEC", 0)

    try:
        path_fd = os.open(path, flags)
    except OSError as e:
        if e.errno in {
            errno.ENOENT,
            errno.ENOTDIR,
            errno.EACCES,
            errno.ELOOP,
        }:
            return False
        raise

    try:
        a = os.fstat(fd)
        b = os.fstat(path_fd)

        return (
            a.st_dev == b.st_dev and
            a.st_ino == b.st_ino and
            stat.S_IFMT(a.st_mode) == stat.S_IFMT(b.st_mode)
        )
    finally:
        os.close(path_fd)
```