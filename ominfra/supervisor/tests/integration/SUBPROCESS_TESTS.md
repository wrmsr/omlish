# Subprocess-Based Integration Tests

## Overview

The supervisor integration tests run supervisor as a **real subprocess** and observe its behavior via:
- **HTTP API** (primary observation mechanism)
- **Log files** (secondary verification)
- **OS primitives** (PIDs, signals, process existence)
- **Exit codes** (shutdown behavior)

**No mocks. No patches. Just real processes.**

## Why Subprocess Tests?

The original in-process test approach hit a fundamental blocker: **signal handling**.

```python
# This fails in pytest:
signal.signal(signal.SIGCHLD, handler)
# ValueError: signal only works in main thread of the main interpreter
```

Since supervisor **must** handle signals (especially SIGCHLD for process reaping), we can't run it in the same process as pytest. Running in a subprocess solves this and gives us:

1. **True end-to-end testing** - Supervisor runs exactly as it would in production
2. **Signal handling works** - Each test's supervisor is in its own process
3. **Better isolation** - Tests can't interfere with each other
4. **Real observability** - HTTP API, logs, and PIDs are all real

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ pytest (main process)                                       │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │ TestSubprocessLifecycle                       │          │
│  │                                               │          │
│  │  1. Write config.json ──────────────┐        │          │
│  │  2. Spawn supervisor subprocess ────┼────────┼─────┐    │
│  │  3. Poll HTTP API ──────────────────┼────────┼──┐  │    │
│  │  4. Verify process states           │        │  │  │    │
│  │  5. Send signals ────────────────────┼────────┼──┼──┼──┐ │
│  │  6. Check logs                       │        │  │  │  │ │
│  │  7. Stop supervisor                  │        │  │  │  │ │
│  └──────────────────────────────────────┼────────┼──┼──┼──┼─┘
│                                         │        │  │  │  │  │
└─────────────────────────────────────────┼────────┼──┼──┼──┼──┘
                                          │        │  │  │  │
                                          ▼        │  │  │  │
            ┌─────────────────────────────────────┼──┼──┼──┼──┐
            │ supervisord subprocess (PID 12345)  │  │  │  │  │
            │                                     │  │  │  │  │
            │  ┌─────────────────┐                │  │  │  │  │
            │  │ HTTP Server     │◄───────────────┘  │  │  │  │
            │  │ :19001          │                   │  │  │  │
            │  └─────────────────┘                   │  │  │  │
            │                                        │  │  │  │
            │  ┌─────────────────┐                   │  │  │  │
            │  │ Log File        │◄──────────────────┘  │  │  │
            │  │ supervisor.log  │                      │  │  │
            │  └─────────────────┘                      │  │  │
            │                                           │  │  │
            │  ┌─────────────────┐                      │  │  │
            │  │ Signal Handler  │◄─────────────────────┘  │  │
            │  │ (SIGTERM, ...)  │                         │  │
            │  └─────────────────┘                         │  │
            │                                              │  │
            │  Manages child processes:                    │  │
            │  ┌──────────────┐ ┌──────────────┐          │  │
            │  │ worker (1234)│ │ runner (5678)│◄─────────┘  │
            │  └──────────────┘ └──────────────┘             │
            └────────────────────────────────────────────────┘
```

## Test Harness

### Base Class: `SupervisorSubprocessTestBase`

All subprocess tests inherit from this class:

```python
class TestMyFeature(SupervisorSubprocessTestBase):
    def test_something(self):
        # Build config
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'worker': {
                            'command': 'python -m my.program',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        # Start supervisor subprocess
        self.start_supervisor(config)

        # Observe via HTTP API
        proc_info = self.wait_for_process_state('worker', 'RUNNING')

        # Verify via OS
        self.assert_process_running(proc_info['pid'])
```

### Key Methods

#### Supervisor Control
- `start_supervisor(config_dict)` - Start supervisor subprocess
- `send_signal(sig)` - Send signal to supervisor
- `get_logs()` - Read log file

#### Observation (via HTTP)
- `get_status()` - Get full status
- `get_process_info(name)` - Get single process info
- `wait_for_process_state(name, state, timeout)` - Poll until state reached

#### Assertions
- `assert_process_running(pid)` - Verify OS-level process exists
- `assert_process_dead(pid, timeout)` - Verify process exited
- `assert_log_contains(text)` - Check log file
- `wait_until(condition, timeout)` - Generic polling

#### Utilities
- `make_config(dict)` - Build config with test defaults
- Auto-allocated HTTP ports (no conflicts)
- Auto-cleaned temp directories

## Observation Mechanisms

### 1. HTTP API (Primary)

The HTTP API is our main window into supervisor state:

```python
status = self.get_status()
# Returns:
{
    'groups': {
        'test': {
            'processes': {
                'worker': {
                    'state': 'RUNNING',
                    'pid': 12345,
                },
            },
        },
    },
    'method': 'GET',
    'path': '/',
}
```

**Pros:**
- Real-time state
- Works across process boundary
- Already implemented
- Network-accessible (could test remote supervisor)

**Limitations:**
- Polling required (can't wait for events directly)
- Limited detail compared to internal events

### 2. Log Files (Secondary)

Log files provide detailed narrative:

```python
logs = self.get_logs()
assert 'entered RUNNING state' in logs
assert 'success: worker' in logs
```

**Pros:**
- Rich detail
- Full history
- Debugging aid

**Limitations:**
- String matching (brittle)
- No structured data
- Delayed writes

### 3. OS Primitives (Direct)

The OS is the source of truth:

```python
# Check if PID exists
self.assert_process_running(pid)

# Send signals
os.kill(pid, signal.SIGUSR1)

# Check exit codes
returncode = self.supervisor_proc.wait()
```

**Pros:**
- Can't be mocked away
- Authoritative
- Fast

**Limitations:**
- Limited information (just alive/dead)
- Race conditions possible

## What's Missing (Future Enhancements)

### 1. HTTP API Enhancements

Current API only supports `GET /` (status).

**Needed:**
- `POST /api/processes/{name}/start` - Start process
- `POST /api/processes/{name}/stop` - Stop process
- `POST /api/processes/{name}/signal` - Send signal
- `GET /api/events?since=N` - Get events (see below)

### 2. JSON Event Logging

Add optional structured event logging to file:

```python
# In supervisor config:
{
    'event_log_file': '/tmp/events.jsonl',  # JSON lines format
}

# Events written as:
{"type": "ProcessStateEvent", "process": "worker", "from": "STARTING", "to": "RUNNING", "ts": 1234.56}
{"type": "ProcessLogEvent", "process": "worker", "channel": "stdout", "data": "...", "ts": 1234.57}

# In tests:
events = self.get_events()
assert any(e['type'] == 'ProcessStateRunningEvent' for e in events)
```

This would enable:
- Event sequence verification
- Timing assertions
- No polling required

### 3. HTTP Event Streaming

Alternative to file-based events:

```python
# GET /api/events?stream=true (SSE or chunked)
# or
# GET /api/events?since=123456789  (poll-based)
```

## Running Tests

```bash
# Run subprocess tests only
./python -m pytest ominfra/supervisor/tests/integration/test_subprocess_*.py -v

# Run specific test
./python -m pytest ominfra/supervisor/tests/integration/test_subprocess_lifecycle.py::TestSubprocessLifecycle::test_process_starts_and_runs -v

# With verbose output
./python -m pytest ominfra/supervisor/tests/integration/test_subprocess_lifecycle.py -v -s
```

## Current Test Coverage

**Converted to subprocess approach:**
- ✅ Basic lifecycle (8 tests)
- ✅ Signals (2 tests)
- ✅ Restart policies (3 tests)

**Total:** 13 tests running in real subprocesses

**Still to convert:**
- Fault tolerance tests
- Logging tests
- HTTP API tests
- Edge cases
- Concurrency tests

## Debugging

### View supervisor output

```python
# In test, before cleanup:
print("SUPERVISOR STDOUT:", self.supervisor_proc.stdout.read())
print("SUPERVISOR STDERR:", self.supervisor_proc.stderr.read())
```

### Check logs

```python
# In test:
print("LOGS:", self.get_logs())
```

### Attach debugger to subprocess

```python
# Add to supervisor code:
import debugpy
debugpy.listen(5678)
print("Waiting for debugger...")
debugpy.wait_for_client()

# Then attach from VS Code/PyCharm to port 5678
```

### Keep temp directory

```python
# In test:
def tearDown(self):
    print(f"TEMP DIR: {self.temp_dir}")
    # Comment out cleanup to inspect files
    # shutil.rmtree(self.temp_dir)
```

## Design Decisions

### Why JSON config instead of ServerConfig objects?

Tests write JSON files because that's how supervisor is invoked in production. This tests the full config loading path.

### Why polling instead of events?

Currently we poll the HTTP API because:
1. No event streaming yet
2. Simple to implement
3. Fast enough (100ms poll interval)

Event streaming would be better long-term but isn't required to get started.

### Why not use supervisorctl?

We could test via `supervisorctl` CLI, but:
- HTTP API is more direct
- Easier to automate
- Don't need to parse CLI output

Though testing `supervisorctl` compatibility would be valuable eventually.

## Migration Strategy

The old in-process tests still exist (`test_process_lifecycle.py`, etc.) but **won't work** due to signal handling.

**Plan:**
1. ✅ Create subprocess test harness
2. ✅ Convert simple tests to validate approach
3. 🔄 Add JSON event logging (optional but helpful)
4. 🔄 Enhance HTTP API for better control
5. Convert remaining tests
6. Delete old in-process tests

No rush - we can have both coexist during migration.
