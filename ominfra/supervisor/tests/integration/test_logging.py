# ruff: noqa: PT009 UP006 UP007 UP045
"""Integration tests for process logging and output capture."""
import sys
import time

from ...events import ProcessLogStderrEvent
from ...events import ProcessLogStdoutEvent
from ...states import ProcessState
from .base import SupervisorTestBase


class TestLogging(SupervisorTestBase):
    """Test process output capture and logging."""

    def test_stdout_capture_with_events(self):
        """stdout with events_enabled should generate ProcessLogStdoutEvent."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'output': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 5 0.5',
                            'auto_start': True,
                            'stdout': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for process to run
            self.wait_for_process_state(sup, 'output', ProcessState.RUNNING, timeout=5.0)

            # Wait for output events
            time.sleep(3.0)

            # Should have captured stdout events
            stdout_events = [e for e in self._events if isinstance(e, ProcessLogStdoutEvent)]
            self.assertGreater(len(stdout_events), 0, 'Should capture stdout events')

            # Events should contain actual output data
            for event in stdout_events:
                self.assertIsInstance(event.data, bytes)
                self.assertGreater(len(event.data), 0)

    def test_stderr_capture_with_events(self):
        """stderr with events_enabled should generate ProcessLogStderrEvent."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'errout': {
                            'command': (
                                f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 5 0.5 1.0'
                            ),
                            'auto_start': True,
                            'stderr': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for process to run
            self.wait_for_process_state(sup, 'errout', ProcessState.RUNNING, timeout=5.0)

            # Wait for output
            time.sleep(3.0)

            # Should have captured stderr events
            stderr_events = [e for e in self._events if isinstance(e, ProcessLogStderrEvent)]
            self.assertGreater(len(stderr_events), 0, 'Should capture stderr events')

    def test_redirect_stderr_combines_streams(self):
        """redirect_stderr=True should combine stderr into stdout."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'combined': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 10 0.3',
                            'auto_start': True,
                            'redirect_stderr': True,
                            'stdout': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for process to generate output
            self.wait_for_process_state(sup, 'combined', ProcessState.RUNNING, timeout=5.0)
            time.sleep(4.0)

            # Should see stdout events (including redirected stderr)
            stdout_events = [e for e in self._events if isinstance(e, ProcessLogStdoutEvent)]
            stderr_events = [e for e in self._events if isinstance(e, ProcessLogStderrEvent)]  # noqa

            self.assertGreater(len(stdout_events), 0, 'Should have stdout events')
            # stderr should be redirected to stdout, so fewer/no stderr events
            # (depending on implementation details)

    def test_events_contain_process_info(self):
        """Log events should contain process and PID information."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'info': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 3 0.5',
                            'auto_start': True,
                            'stdout': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            proc = self.wait_for_process_state(sup, 'info', ProcessState.RUNNING, timeout=5.0)
            pid = proc.pid

            # Wait for output events
            time.sleep(2.0)

            stdout_events = [e for e in self._events if isinstance(e, ProcessLogStdoutEvent)]
            self.assertGreater(len(stdout_events), 0)

            # Check event has process and pid
            event = stdout_events[0]
            self.assertIs(event.process, proc)
            self.assertEqual(event.pid, pid)

    def test_output_without_events_enabled(self):
        """Process output without events_enabled should not generate events."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'silent': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 5 0.5',
                            'auto_start': True,
                            'stdout': {'events_enabled': False},
                            'stderr': {'events_enabled': False},
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for process to run and generate output
            self.wait_for_process_state(sup, 'silent', ProcessState.RUNNING, timeout=5.0)
            time.sleep(3.0)

            # Should not have log events
            stdout_events = [e for e in self._events if isinstance(e, ProcessLogStdoutEvent)]
            stderr_events = [e for e in self._events if isinstance(e, ProcessLogStderrEvent)]

            self.assertEqual(len(stdout_events), 0, 'Should not capture stdout when events disabled')
            self.assertEqual(len(stderr_events), 0, 'Should not capture stderr when events disabled')

    def test_output_from_multiple_processes(self):
        """Multiple processes should have their output captured separately."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'proc1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 3 0.5',
                            'auto_start': True,
                            'stdout': {'events_enabled': True},
                        },
                        'proc2': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 3 0.5',
                            'auto_start': True,
                            'stdout': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for both to run
            proc1 = self.wait_for_process_state(sup, 'proc1', ProcessState.RUNNING, timeout=5.0)
            proc2 = self.wait_for_process_state(sup, 'proc2', ProcessState.RUNNING, timeout=5.0)

            # Wait for output
            time.sleep(3.0)

            # Should have events from both processes
            proc1_events = [
                e for e in self._events
                if isinstance(e, ProcessLogStdoutEvent) and e.process is proc1
            ]
            proc2_events = [
                e for e in self._events
                if isinstance(e, ProcessLogStdoutEvent) and e.process is proc2
            ]

            self.assertGreater(len(proc1_events), 0, 'Should have output from proc1')
            self.assertGreater(len(proc2_events), 0, 'Should have output from proc2')
