# ruff: noqa: PT009 UP006 UP007 UP045
"""Integration tests for basic process lifecycle management."""
import sys
import time

from ...events import ProcessStateBackoffEvent
from ...events import ProcessStateExitedEvent
from ...events import ProcessStateStartingEvent
from ...events import ProcessStateStoppedEvent
from ...states import ProcessState
from .base import SupervisorTestBase


class TestProcessLifecycle(SupervisorTestBase):
    """Test basic process start, run, and stop transitions."""

    def test_process_starts_and_runs(self):
        """Process with auto_start=True should start and reach RUNNING state."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'runner': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10 1',
                            'auto_start': True,
                            'start_secs': 1,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for process to reach RUNNING
            proc = self.wait_for_process_state(sup, 'runner', ProcessState.RUNNING, timeout=5.0)

            # Verify it has a PID
            self.assertIsNotNone(proc.pid)
            self.assertGreater(proc.pid, 0)

            # Verify process is actually alive
            self.assert_process_alive(proc.pid)

            # Verify it stays running for a bit
            time.sleep(2)
            self.assertEqual(proc.state, ProcessState.RUNNING)
            self.assert_process_alive(proc.pid)

    def test_process_with_auto_start_false(self):
        """Process with auto_start=False should remain STOPPED."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'manual': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': False,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=5.0) as sup:
            # Give it time to potentially start (it shouldn't)
            time.sleep(1.0)

            proc = self.get_process(sup, 'manual')
            assert proc is not None
            self.assertEqual(proc.state, ProcessState.STOPPED)
            self.assertEqual(proc.pid, 0)

    def test_process_transitions_through_starting(self):
        """Process should transition STOPPED -> STARTING -> RUNNING."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'slow': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.slow_starter 2 5',
                            'auto_start': True,
                            'start_secs': 3,  # Must stay up for 3s to be RUNNING
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Should see STARTING event
            self.wait_for_event_type(ProcessStateStartingEvent, timeout=3.0)

            # Process should be in STARTING state initially
            proc = self.get_process(sup, 'slow')
            assert proc is not None
            self.assertIn(proc.state, [ProcessState.STARTING, ProcessState.RUNNING])

            # Eventually should reach RUNNING
            proc = self.wait_for_process_state(sup, 'slow', ProcessState.RUNNING, timeout=10.0)
            self.assertGreater(proc.pid, 0)
            self.assert_process_alive(proc.pid)

    def test_process_exits_too_quickly_enters_backoff(self):
        """Process that exits before start_secs should enter BACKOFF."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'quick_exit': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 0.1',
                            'auto_start': True,
                            'start_secs': 2,  # Needs 2s, but exits in 0.1s
                            'start_retries': 3,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should eventually see BACKOFF event
            self.wait_for_event_type(ProcessStateBackoffEvent, timeout=5.0)

            # Process should be in BACKOFF or later state
            proc = self.get_process(sup, 'quick_exit')
            assert proc is not None
            self.assertIn(proc.state, [ProcessState.BACKOFF, ProcessState.STARTING, ProcessState.FATAL])

    def test_process_successful_exit(self):
        """Process that exits with expected code should reach EXITED state."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'short_task': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 2',
                            'auto_start': True,
                            'start_secs': 1,
                            'auto_restart': False,
                            'exitcodes': [0],
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should reach RUNNING first
            self.wait_for_process_state(sup, 'short_task', ProcessState.RUNNING, timeout=5.0)

            # Then should exit
            proc = self.wait_for_process_state(sup, 'short_task', ProcessState.EXITED, timeout=5.0)

            # Should have exited cleanly
            self.assertEqual(proc.pid, 0)

            # Should see EXITED event
            events = [e for e in self._events if isinstance(e, ProcessStateExitedEvent)]
            self.assertGreater(len(events), 0)

    def test_multiple_processes_in_group(self):
        """Multiple processes in same group should all start."""

        config = self.make_config({
            'groups': {
                'multi': {
                    'processes': {
                        'proc1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                        'proc2': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                        'proc3': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # All three should reach RUNNING
            proc1 = self.wait_for_process_state(sup, 'proc1', ProcessState.RUNNING, timeout=5.0)
            proc2 = self.wait_for_process_state(sup, 'proc2', ProcessState.RUNNING, timeout=5.0)
            proc3 = self.wait_for_process_state(sup, 'proc3', ProcessState.RUNNING, timeout=5.0)

            # All should have distinct PIDs
            pids = {proc1.pid, proc2.pid, proc3.pid}
            self.assertEqual(len(pids), 3)

            # All should be alive
            for pid in pids:
                self.assert_process_alive(pid)

    def test_multiple_groups(self):
        """Multiple process groups should all start."""

        config = self.make_config({
            'groups': {
                'group1': {
                    'processes': {
                        'worker': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                    },
                },
                'group2': {
                    'processes': {
                        'worker': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Both should start (same name but different groups)
            proc1 = self.wait_for_process_state(sup, 'group1:worker', ProcessState.RUNNING, timeout=5.0)
            proc2 = self.wait_for_process_state(sup, 'group2:worker', ProcessState.RUNNING, timeout=5.0)

            self.assertNotEqual(proc1.pid, proc2.pid)
            self.assert_process_alive(proc1.pid)
            self.assert_process_alive(proc2.pid)

    def test_process_stop_transition(self):
        """Stopping a running process should transition to STOPPED."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'stoppable': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 60',
                            'auto_start': True,
                            'stop_wait_secs': 5,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Wait for RUNNING
            proc = self.wait_for_process_state(sup, 'stoppable', ProcessState.RUNNING, timeout=5.0)
            pid = proc.pid

            # Stop the process
            proc.stop()

            # Should transition to STOPPED
            self.wait_for_process_state(sup, 'stoppable', ProcessState.STOPPED, timeout=10.0)

            # Process should be dead
            self.assert_process_dead(pid, timeout=2.0)

            # Should see STOPPED event
            self.wait_for_event_type(ProcessStateStoppedEvent, timeout=2.0)

    def test_priority_based_startup_order(self):
        """Processes should start in priority order (lower priority first)."""

        config = self.make_config({
            'groups': {
                'ordered': {
                    'processes': {
                        'third': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 0.5',
                            'auto_start': True,
                            'priority': 300,
                        },
                        'first': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 0.5',
                            'auto_start': True,
                            'priority': 100,
                        },
                        'second': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 0.5',
                            'auto_start': True,
                            'priority': 200,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:  # noqa
            # Collect STARTING events
            time.sleep(2.0)

            starting_events = [
                e for e in self._events
                if isinstance(e, ProcessStateStartingEvent)
            ]

            # Should have at least 3 STARTING events
            self.assertGreaterEqual(len(starting_events), 3)

            # Extract process names in order
            names = [e.process.name for e in starting_events[:3]]

            # Should start in priority order: first (100), second (200), third (300)
            # Note: They might overlap, but first should definitely start before third
            first_idx = names.index('first') if 'first' in names else -1
            third_idx = names.index('third') if 'third' in names else -1

            if first_idx >= 0 and third_idx >= 0:
                self.assertLess(first_idx, third_idx, 'Lower priority should start first')
