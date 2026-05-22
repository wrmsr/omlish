# ruff: noqa: PT009 UP006 UP007 UP045
"""
Subprocess-based test harness for supervisor integration tests.

Runs supervisor in a real subprocess and observes via HTTP API, logs, and OS primitives.
No mocks, no patches - just real processes.
"""
import http.client
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import typing as ta
import unittest

from ...states import ProcessState
from ...utils.ostypes import Pid


##


def get_free_port() -> int:
    """Get a free TCP port."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]
    finally:
        sock.close()


def is_process_running(pid: Pid) -> bool:
    """Check if process with PID exists."""

    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


##


class SupervisorSubprocessTestBase(unittest.TestCase):
    """
    Base class for subprocess-based supervisor integration tests.

    Each test runs supervisor in a real subprocess and observes behavior via:
    - HTTP API (primary)
    - Log files (secondary)
    - OS primitives (PIDs, signals)
    - Exit codes
    """

    def setUp(self) -> None:
        super().setUp()

        # Create temp directory for this test
        self.temp_dir = pathlib.Path(tempfile.mkdtemp(prefix='supervisor_test_'))

        # File paths
        self.config_file = self.temp_dir / 'supervisor.json'
        self.log_file = self.temp_dir / 'supervisord.log'
        self.pid_file = self.temp_dir / 'supervisord.pid'

        # Network
        self.http_port = get_free_port()

        # Supervisor subprocess
        self.supervisor_proc: ta.Optional[subprocess.Popen] = None
        self._supervisor_pid: ta.Optional[Pid] = None

    def tearDown(self) -> None:
        super().tearDown()

        # Stop supervisor if still running
        self._stop_supervisor()

        # Clean up temp directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    #

    def make_config(
            self,
            config_dict: ta.Mapping[str, ta.Any],
            *,
            no_daemon: bool = True,
            **kwargs: ta.Any,
    ) -> ta.Dict[str, ta.Any]:
        """
        Build config dict with test defaults.

        Returns dict (not ServerConfig) since we'll serialize to JSON.
        """

        return {
            'no_daemon': no_daemon,
            'silent': True,
            'no_cleanup': True,
            'log_file': str(self.log_file),
            'pidfile': str(self.pid_file),
            'http_port': self.http_port,
            **config_dict,
            **kwargs,
        }

    def start_supervisor(
            self,
            config_dict: ta.Mapping[str, ta.Any],
            *,
            wait_for_http: bool = True,
            timeout: float = 5.0,
    ) -> None:
        """
        Start supervisor in subprocess.

        Args:
            config_dict: Configuration dictionary
            wait_for_http: Wait for HTTP API to be ready
            timeout: Timeout for HTTP readiness
        """

        # Ensure no supervisor already running
        if self.supervisor_proc is not None:
            raise RuntimeError('Supervisor already running')

        # Write config file
        with open(self.config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)

        # Start supervisor subprocess
        self.supervisor_proc = subprocess.Popen(
            [
                sys.executable,
                '-m',
                'ominfra.supervisor',
                str(self.config_file),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={
                **os.environ,
                'PYTHONPATH': ':'.join([
                    os.getcwd(),
                    *([pp] if (pp := os.environ.get('PYTHONPATH')) else []),
                ]),
                'OMLISH_PYCHARM_RUNHACK_ENABLED': '0',
            },
            cwd=str(self.temp_dir),
        )

        # Give it a moment to start
        time.sleep(0.2)

        # Check if it crashed immediately
        returncode = self.supervisor_proc.poll()
        if returncode is not None:
            stdout, stderr = self.supervisor_proc.communicate()
            raise RuntimeError(
                f'Supervisor exited immediately with code {returncode}\n'
                f'stdout: {stdout.decode()}\n'
                f'stderr: {stderr.decode()}',
            )

        # Wait for HTTP API if requested
        if wait_for_http:
            self._wait_for_http_api(timeout=timeout)

        # Read PID from file
        self._read_supervisor_pid()

    def _wait_for_http_api(self, timeout: float = 5.0) -> None:
        """Poll until HTTP API responds."""

        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                conn = http.client.HTTPConnection('localhost', self.http_port, timeout=1)
                try:
                    conn.request('GET', '/')
                    resp = conn.getresponse()
                    resp.read()  # Consume body
                    if resp.status == 200:
                        return  # Success!
                finally:
                    conn.close()
            except (ConnectionRefusedError, OSError):
                time.sleep(0.1)

        # Timeout - check if supervisor crashed
        if self.supervisor_proc and self.supervisor_proc.poll() is not None:
            stdout, stderr = self.supervisor_proc.communicate()
            raise RuntimeError(
                f'Supervisor crashed during startup\n'
                f'stdout: {stdout.decode()}\n'
                f'stderr: {stderr.decode()}',
            )

        raise TimeoutError(f'Supervisor HTTP API did not start within {timeout}s')

    def _read_supervisor_pid(self) -> None:
        """Read supervisor PID from pidfile."""

        if self.pid_file.exists():
            with open(self.pid_file) as f:
                self._supervisor_pid = Pid(int(f.read().strip()))

    def _stop_supervisor(self, timeout: float = 5.0) -> None:
        """Stop supervisor subprocess."""

        if self.supervisor_proc is None:
            return

        try:
            # Try graceful shutdown
            self.supervisor_proc.terminate()
            self.supervisor_proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            # Force kill
            self.supervisor_proc.kill()
            self.supervisor_proc.wait(timeout=2)
        finally:
            self.supervisor_proc = None
            self._supervisor_pid = None

    #

    def get_status(self) -> ta.Dict[str, ta.Any]:
        """Get supervisor status via HTTP API."""

        conn = http.client.HTTPConnection('localhost', self.http_port, timeout=5)
        try:
            conn.request('GET', '/')
            resp = conn.getresponse()
            if resp.status != 200:
                raise RuntimeError(f'HTTP API returned {resp.status}')
            body = resp.read()
            print(body)
            return json.loads(body)
        finally:
            conn.close()

    def get_process_info(self, name: str) -> ta.Optional[ta.Dict[str, ta.Any]]:
        """
        Get process info from HTTP API.

        Args:
            name: Process name (format: 'group:process' or just 'process')

        Returns:
            Process info dict or None if not found
        """

        status = self.get_status()

        if ':' in name:
            group_name, proc_name = name.split(':', 1)
            group = status.get('groups', {}).get(group_name)
            if group is None:
                return None
            return group.get('processes', {}).get(proc_name)

        else:
            # Search all groups
            for group in status.get('groups', {}).values():
                proc = group.get('processes', {}).get(name)
                if proc is not None:
                    return proc
            return None

    def wait_for_process_state(
            self,
            name: str,
            state: ta.Union[ProcessState, str],
            timeout: float = 5.0,
    ) -> ta.Dict[str, ta.Any]:
        """
        Wait for process to reach state via HTTP polling.

        Args:
            name: Process name
            state: Expected state (ProcessState enum or string)
            timeout: Maximum time to wait

        Returns:
            Process info dict

        Raises:
            AssertionError: If timeout or process not found
        """

        if isinstance(state, ProcessState):
            state_str = state.name
        else:
            state_str = state

        deadline = time.time() + timeout

        while time.time() < deadline:
            proc_info = self.get_process_info(name)

            if proc_info is None:
                time.sleep(0.1)
                continue

            if proc_info.get('state') == state_str:
                return proc_info

            time.sleep(0.1)

        # Timeout
        proc_info = self.get_process_info(name)
        if proc_info is None:
            self.fail(f'Process {name} not found after {timeout}s')
        else:
            self.fail(
                f'Process {name} did not reach state {state_str} within {timeout}s '
                f'(current state: {proc_info.get("state")})',
            )

        raise RuntimeError  # noqa

    #

    def get_logs(self) -> str:
        """Read supervisor log file."""

        if self.log_file.exists():
            return self.log_file.read_text()
        return ''

    def assert_log_contains(self, text: str, message: ta.Optional[str] = None) -> None:
        """Assert log file contains text."""

        logs = self.get_logs()
        if text not in logs:
            self.fail(message or f'Log does not contain: {text}')

    #

    def send_signal(self, sig: int) -> None:
        """Send signal to supervisor process."""

        if self._supervisor_pid is None:
            self._read_supervisor_pid()

        if self._supervisor_pid is None:
            raise RuntimeError('Supervisor PID unknown')

        os.kill(self._supervisor_pid, sig)

    #

    def assert_process_running(self, pid: Pid) -> None:
        """Assert process with PID is running."""

        if not is_process_running(pid):
            self.fail(f'Process {pid} is not running')

    def assert_process_dead(self, pid: Pid, timeout: float = 1.0) -> None:
        """Assert process with PID is dead (with optional wait)."""

        deadline = time.time() + timeout

        while time.time() < deadline:
            if not is_process_running(pid):
                return
            time.sleep(0.1)

        self.fail(f'Process {pid} is still running after {timeout}s')

    def wait_until(
            self,
            condition: ta.Callable[[], bool],
            timeout: float = 5.0,
            interval: float = 0.1,
            message: ta.Optional[str] = None,
    ) -> None:
        """Poll until condition is true or timeout."""

        deadline = time.time() + timeout

        while time.time() < deadline:
            if condition():
                return
            time.sleep(interval)

        self.fail(message or f'Condition not met within {timeout}s')
