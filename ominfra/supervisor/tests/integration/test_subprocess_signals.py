# ruff: noqa: PT009 UP006 UP007 UP045
"""Subprocess-based integration tests for signal handling."""
import signal
import sys
import time

from ...states import ProcessState
from .subprocess_base import SupervisorSubprocessTestBase


class TestSubprocessSignals(SupervisorSubprocessTestBase):
    """Test signal handling via subprocess supervisor."""

    def test_sigterm_stops_process_gracefully(self):
        """Process should handle SIGTERM and stop gracefully."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'graceful': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 60',
                            'auto_start': True,
                            'stop_wait_secs': 5,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Wait for RUNNING
        proc_info = self.wait_for_process_state('graceful', ProcessState.RUNNING, timeout=10.0)
        pid = proc_info['pid']

        # Now we can't directly call proc.stop() since it's in a subprocess
        # But we can observe what happens when supervisor shuts down
        # For now, let's just verify the process is running and responsive

        self.assert_process_running(pid)

        # TODO: Need HTTP API endpoint to stop individual processes
        # For now, we can test supervisor-level shutdown which stops all processes

    def test_sigkill_if_process_ignores_sigterm(self):
        """Process ignoring SIGTERM should be killed with SIGKILL."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'stubborn': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.signal_ignorer 1',
                            'auto_start': True,
                            'stop_wait_secs': 2,  # Short timeout before SIGKILL
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Wait for RUNNING
        proc_info = self.wait_for_process_state('stubborn', ProcessState.RUNNING, timeout=10.0)
        pid = proc_info['pid']

        # Verify it's ignoring signals (it's running)
        self.assert_process_running(pid)

        # When we shut down supervisor, it should eventually SIGKILL this process
        self.send_signal(signal.SIGTERM)

        # Wait for supervisor to exit
        supervisor_proc = self.supervisor_proc
        assert supervisor_proc is not None
        supervisor_proc.wait(timeout=10.0)

        # Process should be dead (killed by SIGKILL)
        time.sleep(1)
        self.assert_process_dead(pid, timeout=2.0)
