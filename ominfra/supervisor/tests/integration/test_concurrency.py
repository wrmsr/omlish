# ruff: noqa: PT009 SLF001 UP006 UP007 UP045
"""Integration tests for concurrent operations."""
import sys
import time

from ...events import Event
from ...groups import ProcessGroupManager
from ...states import ProcessState
from .base import SupervisorTestBase


class TestConcurrency(SupervisorTestBase):
    """Test concurrent process operations and race conditions."""

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

        with self.run_supervisor(config, timeout=15.0) as sup:
            # All should eventually reach RUNNING
            pids = set()
            for i in range(10):
                proc = self.wait_for_process_state(
                    sup,
                    f'concurrent{i}',
                    ProcessState.RUNNING,
                    timeout=10.0,
                )
                pids.add(proc.pid)
                self.assert_process_alive(proc.pid)

            # All PIDs should be unique
            self.assertEqual(len(pids), 10, 'All processes should have unique PIDs')

    def test_multiple_processes_stop_simultaneously(self):
        """Multiple processes stopping at same time should all stop correctly."""
        processes = {
            f'stoppable{i}': {
                'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                'auto_start': True,
                'stop_wait_secs': 5,
            }
            for i in range(5)
        }

        config = self.make_config({
            'groups': {
                'stoppable': {
                    'processes': processes,
                },
            },
        })

        with self.run_supervisor(config, timeout=20.0) as sup:
            # Wait for all to start
            procs = []
            pids = []
            for i in range(5):
                proc = self.wait_for_process_state(
                    sup,
                    f'stoppable{i}',
                    ProcessState.RUNNING,
                    timeout=8.0,
                )
                procs.append(proc)
                pids.append(proc.pid)

            # Stop all simultaneously
            for proc in procs:
                proc.stop()

            # All should eventually stop
            for i in range(5):
                self.wait_for_process_state(
                    sup,
                    f'stoppable{i}',
                    ProcessState.STOPPED,
                    timeout=12.0,
                )

            # All should be dead
            for pid in pids:
                self.assert_process_dead(pid, timeout=2.0)

    def test_start_and_stop_different_processes(self):
        """Starting some processes while stopping others."""
        config = self.make_config({
            'groups': {
                'mixed': {
                    'processes': {
                        'long1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                            'auto_start': True,
                        },
                        'long2': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                            'auto_start': True,
                        },
                        'short1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                            'auto_start': False,  # Start manually
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=20.0) as sup:
            # Wait for auto-start processes
            proc1 = self.wait_for_process_state(sup, 'long1', ProcessState.RUNNING, timeout=5.0)
            proc2 = self.wait_for_process_state(sup, 'long2', ProcessState.RUNNING, timeout=5.0)

            # Now stop one while the other stays running
            proc1.stop()

            # Verify long2 is still running
            time.sleep(1.0)
            self.assertEqual(proc2.state, ProcessState.RUNNING)
            self.assert_process_alive(proc2.pid)

            # Wait for long1 to stop
            self.wait_for_process_state(sup, 'long1', ProcessState.STOPPED, timeout=10.0)

            # long2 should still be running
            self.assertEqual(proc2.state, ProcessState.RUNNING)

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

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Wait for stable processes
            proc1 = self.wait_for_process_state(sup, 'stable1', ProcessState.RUNNING, timeout=5.0)
            proc2 = self.wait_for_process_state(sup, 'stable2', ProcessState.RUNNING, timeout=5.0)

            pid1 = proc1.pid
            pid2 = proc2.pid

            # Wait for crasher to crash and retry
            time.sleep(5.0)

            # Stable processes should still be running
            self.assertEqual(proc1.state, ProcessState.RUNNING)
            self.assertEqual(proc2.state, ProcessState.RUNNING)
            self.assert_process_alive(pid1)
            self.assert_process_alive(pid2)

    def test_process_group_operations_during_transitions(self):
        """Group operations while processes are transitioning."""
        config = self.make_config({
            'groups': {
                'dynamic': {
                    'priority': 100,
                    'processes': {
                        'worker1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.slow_starter 2 10',
                            'auto_start': True,
                            'start_secs': 3,
                        },
                        'worker2': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.slow_starter 2 10',
                            'auto_start': True,
                            'start_secs': 3,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:
            # Processes should be starting
            time.sleep(1.0)

            # Get the group
            groups = sup._process_groups

            if isinstance(groups, ProcessGroupManager):
                group = groups.get('dynamic')
                assert group is not None

                # Try group operations while processes are transitioning
                unstopped = group.get_unstopped_processes()

                # Should see processes (may be STARTING or RUNNING)
                self.assertGreater(len(unstopped), 0)

            # Eventually both should reach RUNNING
            self.wait_for_process_state(sup, 'worker1', ProcessState.RUNNING, timeout=10.0)
            self.wait_for_process_state(sup, 'worker2', ProcessState.RUNNING, timeout=10.0)

    def test_event_callbacks_during_transitions(self):
        """Event callbacks should fire correctly during concurrent transitions."""
        config = self.make_config({
            'groups': {
                'events': {
                    'processes': {
                        'ev1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 1.5',
                            'auto_start': True,
                            'start_secs': 1,
                        },
                        'ev2': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 1.5',
                            'auto_start': True,
                            'start_secs': 1,
                        },
                        'ev3': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 1.5',
                            'auto_start': True,
                            'start_secs': 1,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:  # Noqa
            # Let processes go through their lifecycle
            time.sleep(5.0)

            # Should have received many events
            self.assertGreater(len(self._events), 5, 'Should have multiple events')

            # Events should be well-formed (no corruption from concurrency)
            for event in self._events:
                self.assertIsInstance(event, Event)

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

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Short processes should exit while long is starting/running
            time.sleep(3.0)

            # Long should still be running
            long_proc = self.get_process(sup, 'long')
            assert long_proc is not None

            self.assertEqual(long_proc.state, ProcessState.RUNNING)
            self.assert_process_alive(long_proc.pid)

            # Short processes should be exited
            short1 = self.get_process(sup, 'short1')
            short2 = self.get_process(sup, 'short2')
            assert short1 is not None
            assert short2 is not None

            self.assertEqual(short1.state, ProcessState.EXITED)
            self.assertEqual(short2.state, ProcessState.EXITED)
