# ruff: noqa: PT009 UP006 UP007 UP045
"""
Subprocess-based integration tests for basic process lifecycle.

These tests run supervisor in a real subprocess and observe via HTTP API.
"""
import signal
import sys
import time

from ...states import ProcessState
from .subprocess_base import SupervisorSubprocessTestBase
from .subprocess_base import is_process_running


class TestSubprocessLifecycle(SupervisorSubprocessTestBase):
    """Test basic process lifecycle via subprocess supervisor."""

    def test_process_starts_and_runs(self):
        """Process with auto_start=True should start and reach RUNNING state."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'runner': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30 1',
                            'auto_start': True,
                            'start_secs': 1,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Wait for process to reach RUNNING via HTTP
        proc_info = self.wait_for_process_state('runner', ProcessState.RUNNING, timeout=10.0)

        # Verify it has a PID
        pid = proc_info['pid']
        self.assertIsNotNone(pid)
        self.assertGreater(pid, 0)

        # Verify process is actually running via OS
        self.assert_process_running(pid)

        # Wait a bit, should still be running
        time.sleep(2)

        # Query again
        proc_info2 = self.get_process_info('runner')
        assert proc_info2 is not None
        self.assertEqual(proc_info2['state'], 'RUNNING')
        self.assert_process_running(pid)

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

        self.start_supervisor(config)

        # Give it time to potentially start (it shouldn't)
        time.sleep(2.0)

        # Check status via HTTP
        proc_info = self.get_process_info('manual')
        assert proc_info is not None
        self.assertEqual(proc_info['state'], 'STOPPED')
        self.assertEqual(proc_info['pid'], 0)

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

        self.start_supervisor(config)

        # Should reach RUNNING first
        self.wait_for_process_state('short_task', ProcessState.RUNNING, timeout=5.0)

        # Then should exit
        proc_info = self.wait_for_process_state('short_task', ProcessState.EXITED, timeout=10.0)

        # Should have no PID (not running)
        self.assertEqual(proc_info['pid'], 0)

    def test_multiple_processes_in_group(self):
        """Multiple processes in same group should all start."""
        config = self.make_config({
            'groups': {
                'multi': {
                    'processes': {
                        'proc1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                            'auto_start': True,
                        },
                        'proc2': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                            'auto_start': True,
                        },
                        'proc3': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # All three should reach RUNNING
        proc1 = self.wait_for_process_state('proc1', ProcessState.RUNNING, timeout=10.0)
        proc2 = self.wait_for_process_state('proc2', ProcessState.RUNNING, timeout=10.0)
        proc3 = self.wait_for_process_state('proc3', ProcessState.RUNNING, timeout=10.0)

        # All should have distinct PIDs
        pids = {proc1['pid'], proc2['pid'], proc3['pid']}
        self.assertEqual(len(pids), 3)

        # All should be alive
        for pid in pids:
            self.assert_process_running(pid)

    def test_multiple_groups(self):
        """Multiple process groups should all start."""
        config = self.make_config({
            'groups': {
                'group1': {
                    'processes': {
                        'worker': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                            'auto_start': True,
                        },
                    },
                },
                'group2': {
                    'processes': {
                        'worker': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Both should start (same name but different groups)
        proc1 = self.wait_for_process_state('group1:worker', ProcessState.RUNNING, timeout=10.0)
        proc2 = self.wait_for_process_state('group2:worker', ProcessState.RUNNING, timeout=10.0)

        self.assertNotEqual(proc1['pid'], proc2['pid'])
        self.assert_process_running(proc1['pid'])
        self.assert_process_running(proc2['pid'])

    def test_supervisor_shutdown_via_signal(self):
        """Sending SIGTERM to supervisor should trigger graceful shutdown."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'worker': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 60',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Wait for process to start
        proc_info = self.wait_for_process_state('worker', ProcessState.RUNNING, timeout=10.0)
        worker_pid = proc_info['pid']

        # Send SIGTERM to supervisor
        self.send_signal(signal.SIGTERM)

        # Supervisor should exit
        supervisor_proc = self.supervisor_proc
        assert supervisor_proc is not None
        supervisor_proc.wait(timeout=10.0)
        returncode = supervisor_proc.returncode

        # Should exit cleanly
        self.assertEqual(returncode, 0)

        # Worker process should be stopped
        time.sleep(1)
        self.assertFalse(is_process_running(worker_pid), 'Worker should be stopped')

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

        self.start_supervisor(config)

        # Should eventually enter BACKOFF
        # We'll poll for it since it might cycle through STARTING quickly
        def is_backoff_or_later():
            proc_info = self.get_process_info('quick_exit')
            if proc_info is None:
                return False
            state = proc_info['state']
            return state in ['BACKOFF', 'STARTING', 'FATAL']

        self.wait_until(is_backoff_or_later, timeout=10.0)

        # Should eventually give up and go FATAL
        self.wait_for_process_state('quick_exit', ProcessState.FATAL, timeout=20.0)

    def test_http_api_shows_correct_state(self):
        """HTTP API should accurately reflect process states."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'runner': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                        'stopped': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': False,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Wait for runner to start
        self.wait_for_process_state('runner', ProcessState.RUNNING, timeout=10.0)

        # Get full status
        status = self.get_status()

        # Check structure
        self.assertIn('groups', status)
        self.assertIn('test', status['groups'])
        self.assertIn('processes', status['groups']['test'])

        processes = status['groups']['test']['processes']

        # Runner should be RUNNING
        self.assertEqual(processes['runner']['state'], 'RUNNING')
        self.assertGreater(processes['runner']['pid'], 0)

        # Stopped should be STOPPED
        self.assertEqual(processes['stopped']['state'], 'STOPPED')
        self.assertEqual(processes['stopped']['pid'], 0)
