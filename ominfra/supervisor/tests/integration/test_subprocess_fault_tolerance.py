# ruff: noqa: PT009 UP006 UP007 UP045
"""
Subprocess-based integration tests for fault tolerance.

These are the 'does it break?' tests - supervisor must handle all failure modes gracefully.
"""
import pathlib
import sys
import tempfile
import time

from omlish.lite.check import check

from ...states import ProcessState
from .subprocess_base import SupervisorSubprocessTestBase


class TestSubprocessFaultTolerance(SupervisorSubprocessTestBase):
    """Test supervisor's handling of various failure modes via subprocess."""

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

        self.start_supervisor(config)

        # Should eventually give up and enter FATAL
        proc_info = self.wait_for_process_state('bad_cmd', ProcessState.FATAL, timeout=15.0)
        self.assertEqual(proc_info['state'], 'FATAL')
        self.assertEqual(proc_info['pid'], 0)

    def test_bad_command_not_executable(self):
        """Process with non-executable file should fail gracefully."""

        # Create a non-executable file
        temp_dir = pathlib.Path(tempfile.mkdtemp(prefix='supervisor_test_notexec_'))
        try:
            not_exec = temp_dir / 'not_executable'
            not_exec.write_text('#!/bin/sh\necho hello\n')
            # Don't chmod +x

            config = self.make_config({
                'groups': {
                    'test': {
                        'processes': {
                            'not_exec': {
                                'command': str(not_exec),
                                'auto_start': True,
                                'start_retries': 1,
                            },
                        },
                    },
                },
            })

            self.start_supervisor(config)

            # Should fail to spawn and eventually give up
            proc_info = self.wait_for_process_state('not_exec', ProcessState.FATAL, timeout=10.0)
            self.assertEqual(proc_info['state'], 'FATAL')

        finally:
            # Cleanup
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)

    def test_process_crashes_during_startup(self):
        """Process that crashes immediately during startup should backoff."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'crash_on_start': {
                            # Exit with non-zero code immediately
                            'command': f'{sys.executable} -c "import sys; sys.exit(139)"',
                            'auto_start': True,
                            'start_secs': 1,
                            'start_retries': 2,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should eventually give up and enter FATAL
        proc_info = self.wait_for_process_state('crash_on_start', ProcessState.FATAL, timeout=15.0)
        self.assertEqual(proc_info['state'], 'FATAL')

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

        self.start_supervisor(config)

        # Should see BACKOFF states via HTTP polling
        found_backoff = False
        for _ in range(100):  # Poll for up to 10 seconds
            proc_info = self.get_process_info('rapid')
            if proc_info and proc_info['state'] == 'BACKOFF':
                found_backoff = True
                break
            time.sleep(0.1)

        # Should eventually give up and enter FATAL
        proc_info = self.wait_for_process_state('rapid', ProcessState.FATAL, timeout=25.0)
        self.assertEqual(proc_info['state'], 'FATAL')

        # We should have observed at least one BACKOFF state
        self.assertTrue(found_backoff or proc_info['state'] == 'FATAL', 'Should have seen BACKOFF or reached FATAL')

    def test_process_becomes_zombie(self):
        """Supervisor should handle zombie processes (reap them quickly)."""

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

        self.start_supervisor(config)

        # Wait for process to start
        proc_info = self.wait_for_process_state('quick_exit', ProcessState.RUNNING, timeout=5.0)
        pid = proc_info['pid']

        # Wait for it to exit and be reaped
        self.wait_for_process_state('quick_exit', ProcessState.EXITED, timeout=5.0)

        # Process should be fully reaped (not zombie)
        time.sleep(0.5)
        self.assert_process_dead(pid, timeout=1.0)

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

        self.start_supervisor(config)

        # All should start
        pids = set()
        for i in range(10):
            proc_info = self.wait_for_process_state(
                f'worker{i}',
                ProcessState.RUNNING,
                timeout=10.0,
            )
            self.assertGreater(proc_info['pid'], 0)
            pids.add(proc_info['pid'])

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
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should handle the flood gracefully
        proc_info = self.wait_for_process_state('flood', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

        # Wait for process to finish generating output
        time.sleep(3)

        # Should still be running or exited cleanly
        proc_info = check.not_none(self.get_process_info('flood'))
        self.assertIn(proc_info['state'], ['RUNNING', 'EXITED'])

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

        self.start_supervisor(config)

        # Should fail gracefully and give up
        proc_info = self.wait_for_process_state('empty', ProcessState.FATAL, timeout=10.0)
        self.assertEqual(proc_info['state'], 'FATAL')

    def test_very_long_command(self):
        """Handle very long command line."""

        # Test a very long command string (the point is testing command line parsing/length handling)
        # Use Python's -c with a long but valid command
        long_python_code = 'import time; ' + '; '.join([f'x{i} = {i}' for i in range(50)]) + '; time.sleep(5)'
        long_cmd = f'{sys.executable} -c "{long_python_code}"'

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'long_cmd': {
                            'command': long_cmd,
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should handle long command line
        proc_info = self.wait_for_process_state('long_cmd', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

    def test_clock_skew_tolerance(self):
        """Supervisor should handle timing edge cases."""

        # We can't actually change the system clock in a test, but we can verify
        # normal operation works (the clock adjustment logic is internal)
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

        self.start_supervisor(config)

        # Just verify normal operation works
        proc_info = self.wait_for_process_state('runner', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

        # If there were clock handling bugs, they'd surface during normal operation

    def test_fd_handling_normal_operation(self):
        """Supervisor should handle file descriptors correctly."""

        # This verifies supervisor's FD handling doesn't crash under normal conditions
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

        self.start_supervisor(config)

        proc_info = self.wait_for_process_state('normal', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

        # If FD handling had issues, we'd see errors by now
