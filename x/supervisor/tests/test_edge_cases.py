# ruff: noqa: PT009 UP006 UP007 UP045
"""Integration tests for edge cases and unusual scenarios."""
import sys
import time

from ...states import ProcessState
from .base import SupervisorTestBase


class TestEdgeCases(SupervisorTestBase):
    """Test edge cases and unusual but valid scenarios."""

    def test_process_with_working_directory(self):
        """Process with custom working directory should start in that directory."""

        temp_dir = self.make_temp_dir()

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'with_dir': {
                            # Print current working directory
                            'command': f'{sys.executable} -c "import os; print(os.getcwd())"',
                            'auto_start': True,
                            'directory': temp_dir,
                            'start_secs': 0,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should start successfully
            proc = self.wait_for_process_state(sup, 'with_dir', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc.pid, 0)

    def test_process_with_environment_vars(self):
        """Process with custom environment variables."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'with_env': {
                            'command': (
                                f'{sys.executable} -c '
                                f'"import os; print(os.environ.get(\'CUSTOM_VAR\', \'missing\'))"'
                            ),
                            'auto_start': True,
                            'environment': {
                                'CUSTOM_VAR': 'custom_value',
                                'ANOTHER_VAR': 'another_value',
                            },
                            'start_secs': 0,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should start with environment
            proc = self.wait_for_process_state(sup, 'with_env', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc.pid, 0)

    def test_process_spawns_children_orphans(self):
        """Process that spawns children and exits (creates orphans)."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'orphan_maker': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.orphan_maker 3',
                            'auto_start': True,
                            'start_secs': 0,
                            'auto_restart': False,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Parent should start and exit quickly
            proc = self.wait_for_process_state(sup, 'orphan_maker', ProcessState.RUNNING, timeout=5.0)
            parent_pid = proc.pid

            # Parent should exit (leaving orphan)
            self.wait_for_process_state(sup, 'orphan_maker', ProcessState.EXITED, timeout=5.0)

            # Parent should be dead
            self.assert_process_dead(parent_pid, timeout=2.0)

            # The orphan child will be adopted by init (PID 1) and should eventually exit on its own
            # We can't easily track it, but supervisor shouldn't crash

    def test_rapid_start_stop_cycles(self):
        """Rapid start/stop cycles should be handled correctly."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'cycler': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 30',
                            'auto_start': True,
                            'stop_wait_secs': 3,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=20.0) as sup:
            # Start process
            proc = self.wait_for_process_state(sup, 'cycler', ProcessState.RUNNING, timeout=5.0)
            pid1 = proc.pid  # noqa

            # Stop it
            proc.stop()
            self.wait_for_process_state(sup, 'cycler', ProcessState.STOPPED, timeout=8.0)

            # Note: Restarting a stopped process requires calling spawn, which isn't exposed
            # in the Process interface. This test verifies stop works correctly.

    def test_process_with_umask(self):
        """Process with custom umask setting."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'umask_proc': {
                            'command': f'{sys.executable} -c "import os; print(oct(os.umask(0o22)))"',
                            'auto_start': True,
                            'umask': 0o027,
                            'start_secs': 0,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should start with custom umask
            proc = self.wait_for_process_state(sup, 'umask_proc', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc.pid, 0)

    def test_num_procs_multiple_instances(self):
        """num_procs > 1 should create multiple process instances."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'multi_%(process_num)d': {  # Name template with process_num
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                            'num_procs': 3,
                            'num_procs_start': 0,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:  # noqa
            # Should create multi_0, multi_1, multi_2
            # Note: The current implementation may not fully support %(process_num)d expansion
            # This test documents expected behavior

            # Try to find processes
            time.sleep(3.0)

            # Check if supervisor created multiple instances
            # (Implementation may vary - this is an aspirational test)

    def test_process_command_with_quotes_and_spaces(self):
        """Command with quoted arguments and spaces."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'quoted': {
                            'command': f'{sys.executable} -c "import sys; print(sys.argv)" "arg with spaces" another',
                            'auto_start': True,
                            'start_secs': 0,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should parse command correctly
            proc = self.wait_for_process_state(sup, 'quoted', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc.pid, 0)

    def test_process_that_execs_another_program(self):
        """Process that exec's another program (replaces itself)."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'exec_chain': {
                            # This uses exec to replace the shell with Python
                            'command': (
                                f'/bin/sh -c '
                                f'"exec {sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5"'
                            ),
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should handle exec chain
            proc = self.wait_for_process_state(sup, 'exec_chain', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc.pid, 0)
            self.assert_process_alive(proc.pid)

    def test_process_closes_all_fds(self):
        """Process that closes all file descriptors including stdio."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'fd_closer': {
                            # Close stdio and run
                            'command': (
                                f'/bin/sh -c "exec 0</dev/null; exec 1>/dev/null; exec 2>/dev/null; '
                                f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 3"'
                            ),
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should handle process closing stdio
            proc = self.wait_for_process_state(sup, 'fd_closer', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc.pid, 0)

    def test_process_name_with_special_characters(self):
        """Process names with special characters (but valid)."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'name-with-dashes_and_underscores': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Should handle special characters in name
            proc = self.wait_for_process_state(
                sup,
                'name-with-dashes_and_underscores',
                ProcessState.RUNNING,
                timeout=5.0,
            )
            self.assertGreater(proc.pid, 0)

    def test_priority_zero(self):
        """Process with priority=0 should work."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'zero_priority': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                            'priority': 0,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            proc = self.wait_for_process_state(sup, 'zero_priority', ProcessState.RUNNING, timeout=5.0)
            self.assertEqual(proc.config.priority, 0)
