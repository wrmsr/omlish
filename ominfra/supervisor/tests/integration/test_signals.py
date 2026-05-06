# ruff: noqa: PT009 UP006 UP007 UP045
"""Integration tests for signal handling."""
import signal
import sys
import time

from ...events import ProcessStateStoppingEvent
from ...states import ProcessState
from .base import SupervisorTestBase


class TestSignals(SupervisorTestBase):
    """Test signal handling for processes."""

    def test_sigterm_stops_process_gracefully(self):
        """Process should handle SIGTERM and stop gracefully."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'graceful': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 60',
                            'auto_start': True,
                            'stop_signal': signal.SIGTERM,
                            'stop_wait_secs': 5,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Wait for RUNNING
            proc = self.wait_for_process_state(sup, 'graceful', ProcessState.RUNNING, timeout=5.0)
            pid = proc.pid

            # Stop should send SIGTERM
            proc.stop()

            # Should transition to STOPPING then STOPPED
            self.wait_for_event_type(ProcessStateStoppingEvent, timeout=5.0)
            self.wait_for_process_state(sup, 'graceful', ProcessState.STOPPED, timeout=10.0)

            # Process should be dead
            self.assert_process_dead(pid, timeout=2.0)

    def test_sigkill_if_process_ignores_sigterm(self):
        """Process ignoring SIGTERM should be killed with SIGKILL."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'stubborn': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.signal_ignorer 1',
                            'auto_start': True,
                            'stop_signal': signal.SIGTERM,
                            'stop_wait_secs': 2,  # Short timeout before SIGKILL
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Wait for RUNNING
            proc = self.wait_for_process_state(sup, 'stubborn', ProcessState.RUNNING, timeout=5.0)
            pid = proc.pid

            # Stop - should send SIGTERM, then SIGKILL after stop_wait_secs
            stop_time = time.time()
            proc.stop()

            # Should eventually reach STOPPED (via SIGKILL)
            self.wait_for_process_state(sup, 'stubborn', ProcessState.STOPPED, timeout=10.0)

            # Process should be dead
            self.assert_process_dead(pid, timeout=1.0)

            # Should have taken at least stop_wait_secs
            elapsed = time.time() - stop_time
            self.assertGreaterEqual(elapsed, 2.0, 'Should wait before SIGKILL')

    def test_custom_stop_signal(self):
        """Process with custom stop_signal should receive that signal."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'custom_sig': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 60',
                            'auto_start': True,
                            'stop_signal': signal.SIGINT,  # Custom signal
                            'stop_wait_secs': 5,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Wait for RUNNING
            proc = self.wait_for_process_state(sup, 'custom_sig', ProcessState.RUNNING, timeout=5.0)
            pid = proc.pid

            # Stop should send SIGINT (process handles it gracefully)
            proc.stop()

            # Should stop successfully
            self.wait_for_process_state(sup, 'custom_sig', ProcessState.STOPPED, timeout=10.0)
            self.assert_process_dead(pid, timeout=2.0)

    def test_stop_as_group(self):
        """stop_as_group should send signal to process group."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'group_leader': {
                            # This process spawns a child, creating a process group
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.orphan_maker 10',
                            'auto_start': True,
                            'stop_as_group': True,
                            'stop_wait_secs': 5,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Wait for RUNNING
            proc = self.wait_for_process_state(sup, 'group_leader', ProcessState.RUNNING, timeout=5.0)
            pid = proc.pid

            # Give it time to spawn child
            time.sleep(1.0)

            # Stop with stop_as_group=True
            proc.stop()

            # Should stop
            self.wait_for_process_state(sup, 'group_leader', ProcessState.STOPPED, timeout=10.0)
            self.assert_process_dead(pid, timeout=2.0)

            # Note: With stop_as_group=True, the child should also be killed
            # (We can't easily verify this without tracking the child PID)

    def test_process_signal_without_stopping(self):
        """Sending signal to process without intent to stop."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'signalable': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 60',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Wait for RUNNING
            proc = self.wait_for_process_state(sup, 'signalable', ProcessState.RUNNING, timeout=5.0)
            pid = proc.pid

            # Send SIGUSR1 (process doesn't handle it, but shouldn't crash)
            result = proc.signal(signal.SIGUSR1)

            # Should return None (success)
            self.assertIsNone(result)

            # Process should still be running
            time.sleep(0.5)
            self.assertEqual(proc.state, ProcessState.RUNNING)
            self.assert_process_alive(pid)
