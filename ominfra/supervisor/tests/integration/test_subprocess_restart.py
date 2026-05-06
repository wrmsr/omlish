# ruff: noqa: PT009 UP006 UP007 UP045
"""Subprocess-based integration tests for restart policies."""
import sys
import time

from ...states import ProcessState
from .subprocess_base import SupervisorSubprocessTestBase


class TestSubprocessRestartPolicies(SupervisorSubprocessTestBase):
    """Test auto_restart and retry behavior via subprocess."""

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
                            'start_retries': 5,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should reach RUNNING
        self.wait_for_process_state('crasher', ProcessState.RUNNING, timeout=10.0)

        # Note initial PID
        proc_info = self.get_process_info('crasher')
        assert proc_info is not None
        initial_pid = proc_info['pid']  # noqa

        # Wait for it to crash and restart
        # After crash with unexpected exit code, should enter BACKOFF then restart
        time.sleep(5)

        # Should be running again (possibly with new PID)
        proc_info = self.get_process_info('crasher')
        assert proc_info is not None

        # Should be RUNNING or BACKOFF (retry cycle)
        self.assertIn(proc_info['state'], ['RUNNING', 'BACKOFF', 'STARTING'])

        # Check logs confirm restart behavior
        logs = self.get_logs()
        self.assertIn('entered RUNNING state', logs)

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

        self.start_supervisor(config)

        # Should start and run
        self.wait_for_process_state('no_restart', ProcessState.RUNNING, timeout=10.0)

        # Should exit and stay EXITED
        proc_info = self.wait_for_process_state('no_restart', ProcessState.EXITED, timeout=10.0)  # noqa

        # Wait a bit to ensure no restart
        time.sleep(3)

        # Should still be EXITED
        proc_info2 = self.get_process_info('no_restart')
        assert proc_info2 is not None
        self.assertEqual(proc_info2['state'], 'EXITED')

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

        self.start_supervisor(config)

        # Should eventually give up and enter FATAL
        proc_info = self.wait_for_process_state('retry_limit', ProcessState.FATAL, timeout=30.0)

        # Should be FATAL
        self.assertEqual(proc_info['state'], 'FATAL')
        self.assertEqual(proc_info['pid'], 0)

        # Check logs
        logs = self.get_logs()
        self.assertIn('FATAL', logs)
