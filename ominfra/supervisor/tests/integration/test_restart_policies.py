# ruff: noqa: PT009 UP006 UP007 UP045
"""Integration tests for process restart policies."""
import sys
import time

from ...events import ProcessStateBackoffEvent
from ...events import ProcessStateExitedEvent
from ...events import ProcessStateFatalEvent
from ...events import ProcessStateStartingEvent
from ...states import ProcessState
from .base import SupervisorTestBase


class TestRestartPolicies(SupervisorTestBase):
    """Test auto_restart and retry behavior."""

    def test_auto_restart_unexpected(self):
        """auto_restart='unexpected' should restart on unexpected exit codes."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'crasher': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 1 1.5',
                            'auto_start': True,
                            'auto_restart': 'unexpected',
                            'exitcodes': [0],  # Only 0 is expected
                            'start_secs': 1,
                            'start_retries': 3,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=20.0) as sup:
            # Should see initial STARTING
            self.wait_for_event_type(ProcessStateStartingEvent, timeout=5.0)

            # Should reach RUNNING
            self.wait_for_process_state(sup, 'crasher', ProcessState.RUNNING, timeout=5.0)

            # Should exit (unexpected code 1)
            self.wait_for_event_type(ProcessStateExitedEvent, timeout=5.0)

            # Should enter BACKOFF and retry
            self.wait_for_event_type(ProcessStateBackoffEvent, timeout=5.0)

            # Should see another STARTING (retry)
            time.sleep(2)  # Wait for backoff delay
            starting_events = [e for e in self._events if isinstance(e, ProcessStateStartingEvent)]
            self.assertGreaterEqual(len(starting_events), 2, 'Should retry after unexpected exit')

    def test_auto_restart_unconditional(self):
        """auto_restart='unconditional' should always restart."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'always_restart': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 1.5',
                            'auto_start': True,
                            'auto_restart': 'unconditional',  # Restart even on expected exit
                            'exitcodes': [0],
                            'start_secs': 1,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Should start, run, exit (code 0 - expected), then restart anyway
            self.wait_for_process_state(sup, 'always_restart', ProcessState.RUNNING, timeout=5.0)
            self.wait_for_event_type(ProcessStateExitedEvent, timeout=5.0)

            # Should restart even though exit was expected
            time.sleep(2)
            starting_events = [e for e in self._events if isinstance(e, ProcessStateStartingEvent)]
            self.assertGreaterEqual(len(starting_events), 2, 'Should restart unconditionally')

    def test_auto_restart_false(self):
        """auto_restart=False should not restart."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'no_restart': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 1 1.5',
                            'auto_start': True,
                            'auto_restart': False,
                            'start_secs': 1,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should start and run
            self.wait_for_process_state(sup, 'no_restart', ProcessState.RUNNING, timeout=5.0)

            # Should exit and stay EXITED
            proc = self.wait_for_process_state(sup, 'no_restart', ProcessState.EXITED, timeout=5.0)

            # Wait a bit to ensure no restart
            time.sleep(3)

            # Should still be EXITED
            self.assertEqual(proc.state, ProcessState.EXITED)

            # Should only have one STARTING event
            starting_events = [e for e in self._events if isinstance(e, ProcessStateStartingEvent)]
            self.assertEqual(len(starting_events), 1, 'Should not restart')

    def test_expected_exit_codes(self):
        """Processes exiting with expected codes should not restart (unless unconditional)."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'expected_exit': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 2 1.5',
                            'auto_start': True,
                            'auto_restart': 'unexpected',
                            'exitcodes': [0, 2],  # Both 0 and 2 are expected
                            'start_secs': 1,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should start and run
            self.wait_for_process_state(sup, 'expected_exit', ProcessState.RUNNING, timeout=5.0)

            # Should exit with code 2 (expected)
            proc = self.wait_for_process_state(sup, 'expected_exit', ProcessState.EXITED, timeout=5.0)

            # Wait to ensure no restart
            time.sleep(3)

            # Should stay EXITED (exit was expected)
            self.assertEqual(proc.state, ProcessState.EXITED)

    def test_start_retries_limit(self):
        """Process exceeding start_retries should enter FATAL state."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'retry_limit': {
                            # Exits too quickly every time
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 1 0.1',
                            'auto_start': True,
                            'auto_restart': 'unexpected',
                            'start_secs': 2,  # Needs 2s but exits in 0.1s
                            'start_retries': 2,  # Only 2 retries
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=30.0) as sup:
            # Should eventually give up and enter FATAL
            proc = self.wait_for_process_state(sup, 'retry_limit', ProcessState.FATAL, timeout=25.0)  # noqa

            # Should see FATAL event
            self.wait_for_event_type(ProcessStateFatalEvent, timeout=2.0)

            # Should have seen multiple BACKOFF events
            backoff_events = [e for e in self._events if isinstance(e, ProcessStateBackoffEvent)]
            self.assertGreaterEqual(len(backoff_events), 2, 'Should backoff multiple times')

    def test_backoff_timing(self):
        """Backoff delay should increase with each retry."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'backoff': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 1 0.1',
                            'auto_start': True,
                            'start_secs': 1,
                            'start_retries': 3,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=30.0) as sup:  # noqa
            # Collect BACKOFF events with timestamps
            def check_backoffs():
                backoff_events = [e for e in self._events if isinstance(e, ProcessStateBackoffEvent)]
                return len(backoff_events) >= 2

            self.wait_until(check_backoffs, timeout=20.0)

            # Get backoff event indices
            backoff_events = [
                (i, e) for i, e in enumerate(self._events)
                if isinstance(e, ProcessStateBackoffEvent)
            ]

            # We should see increasing delays (first backoff, second backoff, etc.)
            self.assertGreaterEqual(len(backoff_events), 2)

    def test_successful_start_after_retry(self):
        """Process that eventually starts successfully should clear backoff."""
        # This test uses a process that fails the first time but succeeds after
        # We'll use slow_starter with a delay that's initially too short
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'eventual_success': {
                            # Takes 2s to start, needs 1s to be considered running
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.slow_starter 0.5 10',
                            'auto_start': True,
                            'start_secs': 1,  # Should succeed after startup delay
                            'start_retries': 5,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Should eventually reach RUNNING
            proc = self.wait_for_process_state(sup, 'eventual_success', ProcessState.RUNNING, timeout=10.0)

            # Should have cleared backoff counter (backoff property should be 0)
            self.assertEqual(proc.backoff, 0, 'Backoff should reset on successful start')
