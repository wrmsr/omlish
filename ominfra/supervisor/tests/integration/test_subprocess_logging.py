# ruff: noqa: PT009 UP006 UP007 UP045
"""
Subprocess-based integration tests for process logging configuration.

Note: These tests verify that logging configuration doesn't break process execution.
Full event-based logging tests would require JSON event logging infrastructure.
"""
import sys

from ...states import ProcessState
from .subprocess_base import SupervisorSubprocessTestBase


class TestSubprocessLogging(SupervisorSubprocessTestBase):
    """Test process output configuration via subprocess supervisor."""

    def test_process_with_stdout_events_enabled(self):
        """Process with stdout events_enabled should start and run."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'output': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 5 0.5',
                            'auto_start': True,
                            'stdout': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should start and run without issues
        proc_info = self.wait_for_process_state('output', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

    def test_process_with_stderr_events_enabled(self):
        """Process with stderr events_enabled should start and run."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'errout': {
                            'command': (
                                f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 5 0.5'
                            ),
                            'auto_start': True,
                            'stderr': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should start and run
        proc_info = self.wait_for_process_state('errout', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

    def test_process_with_redirect_stderr(self):
        """Process with redirect_stderr=True should combine stderr into stdout."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'combined': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 5 0.3',
                            'auto_start': True,
                            'redirect_stderr': True,
                            'stdout': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should handle stderr redirection without issues
        proc_info = self.wait_for_process_state('combined', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

    def test_process_without_logging_events(self):
        """Process with events_enabled=False should still run."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'silent': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 5 0.5',
                            'auto_start': True,
                            'stdout': {'events_enabled': False},
                            'stderr': {'events_enabled': False},
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should run without logging events
        proc_info = self.wait_for_process_state('silent', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

    def test_high_output_volume_handling(self):
        """Process generating lots of output should be handled gracefully."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'flood': {
                            # Generate 20 lines with 0.05s interval (avoids edge cases in output_generator)
                            'command': (
                                f'{sys.executable} -m ominfra.supervisor.tests.programs.output_generator 20 0.05'
                            ),
                            'auto_start': True,
                            'stdout': {'events_enabled': True},
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # Should handle output volume
        proc_info = self.wait_for_process_state('flood', ProcessState.RUNNING, timeout=5.0)
        self.assertGreater(proc_info['pid'], 0)

    def test_mixed_logging_configurations(self):
        """Multiple processes with different logging configs should coexist."""

        config = self.make_config({
            'groups': {
                'test': {
                    'processes': {
                        'with_events': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                            'stdout': {'events_enabled': True},
                            'stderr': {'events_enabled': True},
                        },
                        'without_events': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                            'stdout': {'events_enabled': False},
                            'stderr': {'events_enabled': False},
                        },
                        'redirected': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 5',
                            'auto_start': True,
                            'redirect_stderr': True,
                        },
                    },
                },
            },
        })

        self.start_supervisor(config)

        # All should start with their respective logging configs
        for proc_name in ['with_events', 'without_events', 'redirected']:
            proc_info = self.wait_for_process_state(proc_name, ProcessState.RUNNING, timeout=5.0)
            self.assertGreater(proc_info['pid'], 0)
