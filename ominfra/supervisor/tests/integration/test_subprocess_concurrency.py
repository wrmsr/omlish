# ruff: noqa: PT009 UP006 UP007 UP045
"""Subprocess-based integration tests for concurrent operations."""
import sys
import time

from omlish.lite.check import check

from ...states import ProcessState
from .subprocess_base import SupervisorSubprocessTestBase


class TestSubprocessConcurrency(SupervisorSubprocessTestBase):
    """Test concurrent process operations and race conditions via subprocess supervisor."""

    def test_multiple_processes_start_simultaneously(self):
        """Multiple processes starting at same time should all succeed."""

        # Create 10 processes that all auto-start
        processes = {
            f'concurrent{i}': {
                'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                'auto_start': True,
            }
            for i in range(10)
        }

        config = self.make_config({
            'groups': {
                'concurrent': {
                    'processes': processes,
                },
            },
        })

        self.start_supervisor(config)

        # All should eventually reach RUNNING
        pids = set()
        for i in range(10):
            proc_info = self.wait_for_process_state(
                f'concurrent{i}',
                ProcessState.RUNNING,
                timeout=10.0,
            )
            pids.add(proc_info['pid'])
            self.assert_process_running(proc_info['pid'])

        # All PIDs should be unique
        self.assertEqual(len(pids), 10, 'All processes should have unique PIDs')

    def test_process_crashes_while_others_running(self):
        """One process crashing shouldn't affect others."""

        config = self.make_config({
            'groups': {
                'mixed': {
                    'processes': {
                        'stable1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                        'crasher': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.rapid_crasher 1 1',
                            'auto_start': True,
                            'start_retries': 2,
                        },
                        'stable2': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Wait for stable processes
        proc1_info = self.wait_for_process_state('stable1', ProcessState.RUNNING, timeout=5.0)
        proc2_info = self.wait_for_process_state('stable2', ProcessState.RUNNING, timeout=5.0)

        pid1 = proc1_info['pid']
        pid2 = proc2_info['pid']

        # Wait for crasher to crash and retry
        time.sleep(5.0)

        # Stable processes should still be running
        proc1_info = check.not_none(self.get_process_info('stable1'))
        proc2_info = check.not_none(self.get_process_info('stable2'))

        self.assertEqual(proc1_info['state'], 'RUNNING')
        self.assertEqual(proc2_info['state'], 'RUNNING')
        self.assert_process_running(pid1)
        self.assert_process_running(pid2)

    def test_reaping_while_spawning(self):
        """Reaping dead processes while new ones are spawning."""

        config = self.make_config({
            'groups': {
                'churn': {
                    'processes': {
                        'short1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 0.5',
                            'auto_start': True,
                            'start_secs': 0,
                            'auto_restart': False,
                        },
                        'short2': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 0.8',
                            'auto_start': True,
                            'start_secs': 0,
                            'auto_restart': False,
                        },
                        'long': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Short processes should exit while long is starting/running
        time.sleep(3.0)

        # Long should still be running
        long_info = self.get_process_info('long')
        assert long_info is not None
        self.assertEqual(long_info['state'], 'RUNNING')
        self.assert_process_running(long_info['pid'])

        # Short processes should be exited
        short1_info = self.get_process_info('short1')
        short2_info = self.get_process_info('short2')
        assert short1_info is not None
        assert short2_info is not None

        self.assertEqual(short1_info['state'], 'EXITED')
        self.assertEqual(short2_info['state'], 'EXITED')

    def test_mixed_lifecycle_operations(self):
        """Different processes in different lifecycle stages simultaneously."""

        config = self.make_config({
            'groups': {
                'mixed': {
                    'processes': {
                        'quick_exit': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 1.0',
                            'auto_start': True,
                            'start_secs': 0,
                            'auto_restart': False,
                        },
                        'slow_start': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.slow_starter 2 5',
                            'auto_start': True,
                            'start_secs': 3,
                        },
                        'stable': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                        'no_auto_start': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': False,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Wait a bit for mixed states
        time.sleep(3.0)

        # Check states via HTTP API
        status = self.get_status()
        processes = status['groups']['mixed']['processes']

        # quick_exit should be EXITED by now
        self.assertEqual(processes['quick_exit']['state'], 'EXITED')

        # stable should be RUNNING
        self.assertEqual(processes['stable']['state'], 'RUNNING')

        # slow_start might be STARTING or RUNNING depending on timing
        self.assertIn(processes['slow_start']['state'], ['STARTING', 'RUNNING'])

        # no_auto_start should be STOPPED
        self.assertEqual(processes['no_auto_start']['state'], 'STOPPED')

    def test_concurrent_process_exits(self):
        """Multiple processes exiting at similar times."""

        processes = {
            f'exiter{i}': {
                'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 {1.0 + i * 0.2}',
                'auto_start': True,
                'start_secs': 0,
                'auto_restart': False,
            }
            for i in range(5)
        }

        config = self.make_config({
            'groups': {
                'exiters': {
                    'processes': processes,
                },
            },
        })

        self.start_supervisor(config)

        # All should start (start_secs=0 means immediate)
        # Wait for all to exit
        time.sleep(4.0)

        # All should be EXITED now
        status = self.get_status()
        for i in range(5):
            proc_info = status['groups']['exiters']['processes'][f'exiter{i}']
            self.assertEqual(proc_info['state'], 'EXITED')

    def test_supervisor_handles_process_churn(self):
        """Supervisor handles high process churn correctly."""

        config = self.make_config({
            'groups': {
                'churn': {
                    'processes': {
                        'restarter': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 1 0.5',
                            'auto_start': True,
                            'auto_restart': 'unexpected',
                            'exitcodes': [0],
                            'start_secs': 0,
                            'start_retries': 20,  # Allow many retries
                        },
                        'stable': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Wait for stable to start
        stable_info = self.wait_for_process_state('stable', ProcessState.RUNNING, timeout=5.0)
        stable_pid = stable_info['pid']

        # Let restarter churn for a bit
        time.sleep(3.0)

        # Stable should still be running with same PID
        stable_info = check.not_none(self.get_process_info('stable'))
        self.assertEqual(stable_info['state'], 'RUNNING')
        self.assertEqual(stable_info['pid'], stable_pid)
        self.assert_process_running(stable_pid)

        # restarter should be in some restart cycle state
        restarter_info = check.not_none(self.get_process_info('restarter'))
        # Should be actively restarting or in backoff
        self.assertIn(restarter_info['state'], ['STARTING', 'BACKOFF', 'RUNNING', 'EXITED'])
