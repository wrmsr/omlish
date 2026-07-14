# ruff: noqa: PT009 UP006 UP007 UP045
"""Subprocess-based integration tests for restart policies."""
import sys
import time

from omcore.lite.check import check

from ...states import ProcessState
from .subprocess_base import SupervisorSubprocessTestBase


class TestSubprocessRestartPolicies(SupervisorSubprocessTestBase):
    """Test auto_restart and retry behavior via subprocess."""

    def test_auto_restart_unexpected(self):
        """auto_restart='unexpected' should restart on unexpected exit codes."""

        config = self.make_config({
            'groups': [{'name': 'test'}],
            'processes': [
                {
                    'name': 'crasher',
                    'group': 'test',
                    'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 1 1.5',
                    'auto_start': True,
                    'auto_restart': 'unexpected',
                    'exitcodes': [0],  # Only 0 is expected
                    'start_secs': 1,
                    'start_retries': 10,
                },
            ],
        })

        self.start_supervisor(config)

        # Should reach RUNNING
        proc_info = self.wait_for_process_state('crasher', ProcessState.RUNNING, timeout=10.0)
        initial_pid = proc_info['pid']

        # Wait for process to exit with unexpected code 1
        # Process needs 1s to reach RUNNING, then runs for 0.5s more, exits at ~1.5s total
        time.sleep(3)

        # Should have exited and entered restart cycle
        # Expected sequence: RUNNING -> EXITED -> BACKOFF -> STARTING -> RUNNING
        proc_info = check.not_none(self.get_process_info('crasher'))

        # Due to auto_restart='unexpected' and exit code 1 (not in exitcodes=[0]),
        # should be restarting: either BACKOFF, STARTING, or already RUNNING again
        # Poll for up to 5 seconds to catch it in any of these states
        found_restart_evidence = False
        for _ in range(50):  # 5 seconds of polling
            proc_info = check.not_none(self.get_process_info('crasher'))
            if proc_info['state'] in ['BACKOFF', 'STARTING']:
                found_restart_evidence = True
                break
            elif proc_info['state'] == 'RUNNING' and proc_info['pid'] != initial_pid:
                found_restart_evidence = True  # Restarted with new PID
                break
            time.sleep(0.1)

        self.assertTrue(
            found_restart_evidence,
            f"Expected restart behavior but process stayed in {proc_info['state']}",
        )

    def test_auto_restart_false(self):
        """auto_restart=False should not restart."""

        config = self.make_config({
            'groups': [{'name': 'test'}],
            'processes': [
                {
                    'name': 'no_restart',
                    'group': 'test',
                    'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 1.5',
                    'auto_start': True,
                    'auto_restart': False,
                    'start_secs': 1,
                },
            ],
        })

        self.start_supervisor(config)

        # Should start and run
        self.wait_for_process_state('no_restart', ProcessState.RUNNING, timeout=10.0)

        # Should exit successfully and enter EXITED state
        proc_info = self.wait_for_process_state('no_restart', ProcessState.EXITED, timeout=10.0)
        self.assertEqual(proc_info['state'], 'EXITED')

        # Wait a bit to ensure no restart
        time.sleep(2)

        # Should still be EXITED
        proc_info2 = self.get_process_info('no_restart')
        assert proc_info2 is not None
        self.assertEqual(proc_info2['state'], 'EXITED')

    def test_start_retries_limit(self):
        """Process exceeding start_retries should enter FATAL state."""

        config = self.make_config({
            'groups': [{'name': 'test'}],
            'processes': [
                {
                    'name': 'retry_limit',
                    'group': 'test',
                    # Exits too quickly every time
                    'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 1 0.1',
                    'auto_start': True,
                    'auto_restart': 'unexpected',
                    'start_secs': 2,  # Needs 2s but exits in 0.1s
                    'start_retries': 2,  # Only 2 retries
                },
            ],
        })

        self.start_supervisor(config)

        # Should eventually give up and enter FATAL
        # This will go through: STARTING -> BACKOFF -> STARTING -> BACKOFF -> STARTING -> FATAL
        proc_info = self.wait_for_process_state('retry_limit', ProcessState.FATAL, timeout=30.0)

        # Should be FATAL with no PID
        self.assertEqual(proc_info['state'], 'FATAL')
        self.assertEqual(proc_info['pid'], 0)
