# Supervisor Integration Test Suite

Comprehensive, mock-free integration tests for the supervisor process manager.

## Philosophy

These tests use **real processes, real signals, and real OS behavior**. No mocks, no patches. If supervisor claims to manage processes, we test it by actually managing real processes.

## Test Structure

```
integration/
├── base.py                      # Test harness base class
├── test_process_lifecycle.py   # Basic process start/stop/states
├── test_signals.py              # Signal handling (SIGTERM, SIGKILL, etc.)
├── test_restart_policies.py    # auto_restart, retries, backoff
├── test_fault_tolerance.py     # Error handling, crashes, edge cases
├── test_logging.py              # Output capture and logging
├── test_http_api.py             # HTTP status API
├── test_edge_cases.py           # Unusual but valid scenarios
└── test_concurrency.py          # Concurrent operations

programs/                        # Test fixture programs
├── long_runner.py               # Runs for N seconds
├── immediate_exit.py            # Exits with configurable code
├── signal_ignorer.py            # Ignores SIGTERM
├── rapid_crasher.py             # Crashes immediately
├── slow_starter.py              # Takes time to start
├── output_generator.py          # Generates stdout/stderr
├── stdin_echo.py                # Echoes stdin
├── orphan_maker.py              # Spawns children
└── helpers.py                   # Shared utilities
```

## Running Tests

### Run all integration tests
```bash
./python -m pytest ominfra/supervisor/tests/integration/ -v
```

### Run specific test file
```bash
./python -m pytest ominfra/supervisor/tests/integration/test_process_lifecycle.py -v
```

### Run specific test
```bash
./python -m pytest ominfra/supervisor/tests/integration/test_signals.py::TestSignals::test_sigterm_stops_process_gracefully -v
```

### Run with coverage
```bash
./python -m pytest ominfra/supervisor/tests/integration/ --cov=ominfra.supervisor --cov-report=html
```

### Run fault tolerance tests only (longer, more intensive)
```bash
./python -m pytest ominfra/supervisor/tests/integration/test_fault_tolerance.py -v
```

### Stress test (run tests multiple times)
```bash
./python -m pytest ominfra/supervisor/tests/integration/test_concurrency.py --count=10 -v
```

## Test Categories

### Phase 1: Process Lifecycle (test_process_lifecycle.py)
- ✓ Basic start/stop transitions
- ✓ State machine validation (STOPPED → STARTING → RUNNING → STOPPED)
- ✓ auto_start behavior
- ✓ Multiple processes and groups
- ✓ Priority-based ordering

### Phase 2: Signal Handling (test_signals.py, test_restart_policies.py)
- ✓ SIGTERM graceful shutdown
- ✓ SIGKILL escalation for stubborn processes
- ✓ Custom stop signals
- ✓ Process group signaling (stop_as_group)
- ✓ auto_restart policies (unexpected, unconditional, false)
- ✓ Retry limits and backoff timing

### Phase 3: Fault Tolerance (test_fault_tolerance.py)
- ✓ Bad commands (not found, not executable)
- ✓ Process crashes during startup
- ✓ Rapid repeated crashes
- ✓ Zombie process handling
- ✓ Clock skew handling
- ✓ Broken pipes
- ✓ Many processes
- ✓ Output flooding
- ✓ Empty/malformed commands

### Phase 4: Features (test_logging.py, test_http_api.py)
- ✓ stdout/stderr capture with events
- ✓ redirect_stderr
- ✓ Event callbacks
- ✓ HTTP status endpoint
- ✓ Real-time state reflection in API
- ✓ Concurrent HTTP connections

### Phase 5: Edge Cases (test_edge_cases.py, test_concurrency.py)
- ✓ Custom working directory
- ✓ Environment variables
- ✓ Orphaned children
- ✓ Process umask
- ✓ Quoted commands with spaces
- ✓ Multiple processes starting simultaneously
- ✓ Stopping while others running
- ✓ Event callbacks during transitions

## Test Fixtures (programs/)

Simple, predictable Python programs that supervisor manages during tests:

- **long_runner.py** - Runs for specified duration, handles signals gracefully
- **immediate_exit.py** - Exits immediately with configurable exit code
- **signal_ignorer.py** - Ignores SIGTERM to test SIGKILL escalation
- **rapid_crasher.py** - Crashes repeatedly to test backoff logic
- **slow_starter.py** - Takes time to "start up" to test start_secs
- **output_generator.py** - Generates predictable stdout/stderr
- **stdin_echo.py** - Echoes stdin to test process input
- **orphan_maker.py** - Spawns children to test orphan handling

All test programs:
- Log their state clearly to stdout/stderr
- Handle signals appropriately (or intentionally don't)
- Exit with predictable codes
- Are invoked via `python -m ominfra.supervisor.tests.programs.PROGRAM_NAME`

## Test Harness (base.py)

`SupervisorTestBase` provides:

### Supervisor Control
- `run_supervisor(config, timeout=...)` - Run supervisor in controlled environment
- `get_process(supervisor, name)` - Get process by name
- `wait_for_process_state(sup, name, state, timeout)` - Wait for state transition
- `wait_for_event_type(event_type, timeout)` - Wait for specific event
- `wait_for_event_sequence(types, timeout)` - Wait for event sequence

### Assertions
- `assert_process_alive(pid)` - Verify process is running
- `assert_process_dead(pid, timeout)` - Verify process has exited
- `wait_until(condition, timeout)` - Poll until condition is true

### Utilities
- `make_config(dict)` - Build ServerConfig from dict with test defaults
- `make_temp_dir()` - Create temp directory (auto-cleaned)
- Automatic event capture in `self._events`
- Automatic cleanup of spawned processes

## Writing New Tests

Example test:

```python
def test_my_feature(self):
    """Test description."""
    config = self.make_config({
        'groups': {
            'test': {
                'processes': {
                    'my_proc': {
                        'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                        'auto_start': True,
                    },
                },
            },
        },
    })

    with self.run_supervisor(config, timeout=15.0) as sup:
        # Wait for expected state
        proc = self.wait_for_process_state(sup, 'my_proc', ProcessState.RUNNING, timeout=5.0)

        # Verify behavior
        self.assertGreater(proc.pid, 0)
        self.assert_process_alive(proc.pid)

        # Check events
        self.wait_for_event_type(ProcessStateRunningEvent, timeout=2.0)
```

## Guidelines

1. **Real behavior, real validation**: Test with actual processes and OS signals
2. **Deterministic where possible**: Use controlled timing and predictable exit codes
3. **Fast feedback**: Most tests complete in <10 seconds
4. **Isolated**: Each test gets fresh supervisor instance
5. **Observable**: Test programs log their state clearly
6. **Cleanup paranoia**: Always clean up processes, even on failure

## Troubleshooting

### Tests hang
- Check timeout values in `run_supervisor(timeout=...)` and `wait_for_*` calls
- Verify test programs exit properly
- Check for zombie processes: `ps aux | grep python`

### Flaky tests
- Increase timeouts if running on slow hardware
- Check for race conditions in event assertions
- Verify test programs are deterministic

### Process leaks
- Tests should auto-cleanup via `run_supervisor` context manager
- Manually kill: `pkill -f "supervisor.tests.programs"`

## Coverage

Current test coverage includes:
- ✓ 60+ integration tests
- ✓ All major state transitions
- ✓ Signal handling
- ✓ Restart policies
- ✓ Fault tolerance
- ✓ Concurrent operations
- ✓ HTTP API

Areas for expansion:
- [ ] User/UID switching (requires root)
- [ ] Resource limit testing (ulimit)
- [ ] Log file rotation (once implemented)
- [ ] Config reloading (once implemented)
- [ ] num_procs expansion (once fully implemented)
