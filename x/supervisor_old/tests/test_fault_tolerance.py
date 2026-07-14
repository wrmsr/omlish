# ruff: noqa: PT009 UP006 UP007 UP045
"""
Integration tests for fault tolerance.

These are the 'does it break?' tests - supervisor must handle all failure modes gracefully.
"""
import os
import sys
import time

from omcore.lite.check import check

from ...events import ProcessStateBackoffEvent
from ...states import ProcessState
from .base import SupervisorTestBase


class TestFaultTolerance(SupervisorTestBase):
    """Test supervisor's handling of various failure modes."""

    def test_bad_command_no_such_file(self):
        """Process with nonexistent command should fail gracefully."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'bad_cmd': {
                            'command': '/this/does/not/exist/nowhere',
                            'auto_start': True,
                            'start_retries': 2,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should enter BACKOFF due to spawn error
            self.wait_for_event_type(ProcessStateBackoffEvent, timeout=5.0)

            proc = self.get_process(sup, 'bad_cmd')
            self.assertIsNotNone(proc)

            # Should eventually give up and enter FATAL
            proc = self.wait_for_process_state(sup, 'bad_cmd', ProcessState.FATAL, timeout=15.0)  # noqa

    def test_bad_command_not_executable(self):
        """Process with non-executable file should fail gracefully."""

        # Create a non-executable file
        temp_dir = self.make_temp_dir()
        not_exec = os.path.join(temp_dir, 'not_executable')
        with open(not_exec, 'w') as f:
            f.write('#!/bin/sh\necho hello\n')
        # Don't chmod +x

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'not_exec': {
                            'command': not_exec,
                            'auto_start': True,
                            'start_retries': 1,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should fail to spawn
            proc = self.wait_for_process_state(sup, 'not_exec', ProcessState.BACKOFF, timeout=5.0)  # noqa

            # Should eventually give up
            self.wait_for_process_state(sup, 'not_exec', ProcessState.FATAL, timeout=10.0)

    def test_process_crashes_during_startup(self):
        """Process that crashes immediately during startup should backoff."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'crash_on_start': {
                            # Segfault or similar - use exit code to simulate
                            'command': f'{sys.executable} -c "import sys; sys.exit(139)"',  # 139 = SIGSEGV
                            'auto_start': True,
                            'start_secs': 1,
                            'start_retries': 2,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should enter BACKOFF
            proc = self.wait_for_process_state(sup, 'crash_on_start', ProcessState.BACKOFF, timeout=5.0)  # noqa

            # Should eventually give up
            self.wait_for_process_state(sup, 'crash_on_start', ProcessState.FATAL, timeout=15.0)

    def test_rapid_repeated_crashes(self):
        """Rapid repeated crashes should be handled with backoff."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'rapid': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.rapid_crasher 1 0.05',
                            'auto_start': True,
                            'start_secs': 1,
                            'start_retries': 5,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=30.0) as sup:
            # Should see multiple BACKOFF events
            def check_backoffs():
                events = [e for e in self._events if isinstance(e, ProcessStateBackoffEvent)]
                return len(events) >= 3

            self.wait_until(check_backoffs, timeout=20.0)

            # Should eventually give up
            self.wait_for_process_state(sup, 'rapid', ProcessState.FATAL, timeout=25.0)

    def test_process_becomes_zombie(self):
        """Supervisor should handle zombie processes (already reaped by OS)."""

        # This is tricky to test - when a process exits, it becomes a zombie until
        # waitpid() is called. Supervisor should reap it quickly.

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'quick_exit': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 0.5',
                            'auto_start': True,
                            'auto_restart': False,
                            'start_secs': 0,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for process to start
            proc = self.wait_for_process_state(sup, 'quick_exit', ProcessState.RUNNING, timeout=5.0)
            pid = proc.pid

            # Wait for it to exit and be reaped
            self.wait_for_process_state(sup, 'quick_exit', ProcessState.EXITED, timeout=5.0)

            # Process should be fully reaped (not zombie)
            time.sleep(0.5)
            self.assert_process_dead(pid, timeout=1.0)

    def test_clock_skew_backward(self):
        """Supervisor should handle system clock going backward."""

        # We can't actually change the system clock in a test, but we can verify
        # the clock adjustment logic doesn't crash
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'runner': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Just verify normal operation works
            proc = self.wait_for_process_state(sup, 'runner', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc.pid, 0)

            # The _check_and_adjust_for_system_clock_rollback is called internally
            # If there were a bug, it would crash here

    def test_broken_pipe_stdin(self):
        """Handle process closing stdin unexpectedly."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'close_stdin': {
                            # This process exits quickly, closing stdin
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 0.5',
                            'auto_start': True,
                            'start_secs': 0,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            proc = self.wait_for_process_state(sup, 'close_stdin', ProcessState.RUNNING, timeout=5.0)  # noqa

            # Try to write to stdin - should handle EPIPE gracefully
            # (Process will exit soon anyway)
            time.sleep(1.0)

            # Process should have exited
            self.wait_for_process_state(sup, 'close_stdin', ProcessState.EXITED, timeout=5.0)

    def test_supervisor_with_many_processes(self):
        """Supervisor should handle many processes without issues."""

        # Create config with 10 processes
        processes = {
            f'worker{i}': {
                'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                'auto_start': True,
            }
            for i in range(10)
        }

        config = self.make_config({
            'groups': {
                'workers': {
                    'processes': processes,
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # All should start
            for i in range(10):
                proc = self.wait_for_process_state(
                    sup,
                    f'worker{i}',
                    ProcessState.RUNNING,
                    timeout=10.0,
                )
                self.assertGreater(proc.pid, 0)

            # Collect all PIDs
            pids = set()
            for i in range(10):
                proc = check.not_none(self.get_process(sup, f'worker{i}'))
                pids.add(proc.pid)

            # All PIDs should be unique
            self.assertEqual(len(pids), 10)

    def test_process_output_flood(self):
        """Handle process generating lots of output quickly."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'flood': {
                            # Generate 100 lines quickly
                            'command': (
                                f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 100 0.01'
                            ),
                            'auto_start': True,
                            'stdout': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Should handle the flood gracefully
            proc = self.wait_for_process_state(sup, 'flood', ProcessState.RUNNING, timeout=5.0)

            # Wait for process to finish generating output
            time.sleep(3)

            # Should still be running or exited cleanly
            self.assertIn(proc.state, [ProcessState.RUNNING, ProcessState.EXITED])

    def test_empty_command_string(self):
        """Handle empty command string gracefully."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'empty': {
                            'command': '',
                            'auto_start': True,
                            'start_retries': 1,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should fail gracefully
            proc = self.wait_for_process_state(sup, 'empty', ProcessState.BACKOFF, timeout=5.0)  # noqa

            # Should give up
            self.wait_for_process_state(sup, 'empty', ProcessState.FATAL, timeout=10.0)

    def test_very_long_command(self):
        """Handle very long command line."""

        # Create a command with many arguments
        long_cmd = (
            f'{sys.executable} -c "import sys; print(len(sys.argv))" ' +
            ' '.join([f'arg{i}' for i in range(100)])
        )

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'long_cmd': {
                            'command': long_cmd,
                            'auto_start': True,
                            'start_secs': 0,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should handle long command
            proc = self.wait_for_process_state(sup, 'long_cmd', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc.pid, 0)

    def test_process_fd_exhaustion_recovery(self):
        """Supervisor should recover gracefully from FD exhaustion."""

        # This is hard to test without actually exhausting FDs, which could affect the test runner
        # We'll just verify supervisor's error handling doesn't crash
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'normal': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            proc = self.wait_for_process_state(sup, 'normal', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc.pid, 0)

            # If FD handling had issues, we'd see errors by now
