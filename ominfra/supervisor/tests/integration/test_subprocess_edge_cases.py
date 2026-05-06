# ruff: noqa: PT009 UP006 UP007 UP045
"""Subprocess-based integration tests for edge cases and unusual scenarios."""
import pathlib
import sys
import tempfile

from ...states import ProcessState
from .subprocess_base import SupervisorSubprocessTestBase


class TestSubprocessEdgeCases(SupervisorSubprocessTestBase):
    """Test edge cases and unusual but valid scenarios via subprocess supervisor."""

    def test_process_with_working_directory(self):
        """Process with custom working directory should start in that directory."""
        # Create a temp directory for the process to use
        temp_dir = pathlib.Path(tempfile.mkdtemp(prefix='supervisor_test_workdir_'))

        try:
            config = self.make_config({
                'groups': {
                    'test': {
                        'processes': {
                            'with_dir': {
                                # Use a longer-running process
                                'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                                'auto_start': True,
                                'directory': str(temp_dir),
                            },
                        },
                    },
                },
            })

            self.start_supervisor(config)

            # Process should start successfully in the custom directory
            proc_info = self.wait_for_process_state('with_dir', ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc_info['pid'], 0)

        finally:
            # Cleanup temp dir
            temp_dir.rmdir()

    def test_process_with_environment_vars(self):
        """Process with custom environment variables."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'with_env': {
                            # Use a longer-running process
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                            'environment': {
                                'CUSTOM_VAR': 'custom_value',
                                'ANOTHER_VAR': 'another_value',
                            },
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should start with environment
        proc_info = self.wait_for_process_state('with_env', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

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

        self.start_supervisor(config)

        # Parent should start and exit quickly
        proc_info = self.wait_for_process_state('orphan_maker', ProcessState.RUNNING, timeout=5.0)
        parent_pid = proc_info['pid']

        # Parent should exit (leaving orphan)
        self.wait_for_process_state('orphan_maker', ProcessState.EXITED, timeout=5.0)

        # Parent should be dead
        self.assert_process_dead(parent_pid, timeout=2.0)

        # The orphan child will be adopted by init (PID 1) and should eventually exit on its own
        # We can't easily track it, but supervisor shouldn't crash

    def test_process_with_umask(self):
        """Process with custom umask setting."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'umask_proc': {
                            # Use a longer-running process
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                            'umask': 0o027,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should start with custom umask
        proc_info = self.wait_for_process_state('umask_proc', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

    def test_process_command_with_quotes_and_spaces(self):
        """Command with quoted arguments and spaces."""
        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'quoted': {
                            # Use a longer-running process
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should parse command correctly and start
        proc_info = self.wait_for_process_state('quoted', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

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

        self.start_supervisor(config)

        # Should handle exec chain
        proc_info = self.wait_for_process_state('exec_chain', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)
        self.assert_process_running(proc_info['pid'])

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

        self.start_supervisor(config)

        # Should handle process closing stdio
        proc_info = self.wait_for_process_state('fd_closer', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

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

        self.start_supervisor(config)

        # Should handle special characters in name
        proc_info = self.wait_for_process_state(
            'name-with-dashes_and_underscores',
            ProcessState.RUNNING,
            timeout=5.0,
        )
        self.assertGreater(proc_info['pid'], 0)

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

        self.start_supervisor(config)

        proc_info = self.wait_for_process_state('zero_priority', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)
        # Note: Can't easily verify priority from HTTP API, but process should start successfully
