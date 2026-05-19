# ruff: noqa: PT009 UP006 UP007 UP045
"""Subprocess-based integration tests for HTTP API."""
import http.client
import json
import sys
import time

from ...states import ProcessState
from .subprocess_base import SupervisorSubprocessTestBase


class TestSubprocessHttpApi(SupervisorSubprocessTestBase):
    """Test HTTP status API via subprocess supervisor."""

    def test_http_server_starts(self):
        """HTTP server should start and be accessible."""

        config = self.make_config({
            'groups': [{'name': 'test'}],
            'processes': [
                {
                    'name': 'dummy',
                    'group': 'test',
                    'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                    'auto_start': True,
                },
            ],
        })

        self.start_supervisor(config)

        # Wait for process to start
        self.wait_for_process_state('dummy', ProcessState.RUNNING, timeout=5.0)

        # HTTP server should already be responding (we waited for it in start_supervisor)
        # Make another request to verify it's still working
        conn = http.client.HTTPConnection('localhost', self.http_port, timeout=5)
        try:
            conn.request('GET', '/')
            resp = conn.getresponse()

            # Should get a response
            self.assertEqual(resp.status, 200)

            # Should be JSON
            content_type = resp.getheader('Content-Type')
            assert content_type is not None
            self.assertIn('json', content_type.lower())

            # Read and parse body
            body = resp.read()
            data = json.loads(body)

            # Should have structure
            self.assertIn('groups', data)

        finally:
            conn.close()

    def test_http_shows_process_state(self):
        """HTTP API should show current process states."""

        config = self.make_config({
            'groups': [{'name': 'workers'}],
            'processes': [
                {
                    'name': 'worker1',
                    'group': 'workers',
                    'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                    'auto_start': True,
                },
                {
                    'name': 'worker2',
                    'group': 'workers',
                    'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                    'auto_start': True,
                },
            ],
        })

        self.start_supervisor(config)

        # Wait for processes to start
        proc1_info = self.wait_for_process_state('worker1', ProcessState.RUNNING, timeout=5.0)
        proc2_info = self.wait_for_process_state('worker2', ProcessState.RUNNING, timeout=5.0)

        # Query HTTP API
        status = self.get_status()

        # Check structure
        self.assertIn('groups', status)
        self.assertIn('workers', status['groups'])

        workers_group = status['groups']['workers']
        self.assertIn('processes', workers_group)

        processes = workers_group['processes']
        self.assertIn('worker1', processes)
        self.assertIn('worker2', processes)

        # Check process details
        worker1_info = processes['worker1']
        self.assertEqual(worker1_info['state'], 'RUNNING')
        self.assertEqual(worker1_info['pid'], proc1_info['pid'])

        worker2_info = processes['worker2']
        self.assertEqual(worker2_info['state'], 'RUNNING')
        self.assertEqual(worker2_info['pid'], proc2_info['pid'])

    def test_http_shows_state_transitions(self):
        """HTTP API should reflect real-time state changes."""

        config = self.make_config({
            'groups': [{'name': 'test'}],
            'processes': [
                {
                    'name': 'transient',
                    'group': 'test',
                    'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 2',
                    'auto_start': True,
                    'start_secs': 1,
                    'auto_restart': False,
                },
            ],
        })

        self.start_supervisor(config)

        # Wait for RUNNING
        self.wait_for_process_state('transient', ProcessState.RUNNING, timeout=5.0)

        # Query while running
        proc_info = self.get_process_info('transient')
        assert proc_info is not None
        self.assertEqual(proc_info['state'], 'RUNNING')
        self.assertGreater(proc_info['pid'], 0)

        # Wait for process to exit
        self.wait_for_process_state('transient', ProcessState.EXITED, timeout=5.0)

        # Query after exited
        proc_info = self.get_process_info('transient')
        assert proc_info is not None
        self.assertEqual(proc_info['state'], 'EXITED')
        self.assertEqual(proc_info['pid'], 0)  # No PID when not running

    def test_http_concurrent_connections(self):
        """HTTP server should handle concurrent connections."""

        config = self.make_config({
            'groups': [{'name': 'test'}],
            'processes': [
                {
                    'name': 'stable',
                    'group': 'test',
                    'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                    'auto_start': True,
                },
            ],
        })

        self.start_supervisor(config)

        # Wait for process
        self.wait_for_process_state('stable', ProcessState.RUNNING, timeout=5.0)

        # Make multiple concurrent requests
        responses = []
        for _ in range(5):
            conn = http.client.HTTPConnection('localhost', self.http_port, timeout=5)
            try:
                conn.request('GET', '/')
                resp = conn.getresponse()
                responses.append(resp.status)
                resp.read()  # Consume body
            finally:
                conn.close()

        # All should succeed
        self.assertEqual(responses, [200] * 5)

    def test_http_survives_process_crash(self):
        """HTTP server should continue working even if processes crash."""

        config = self.make_config({
            'groups': [{'name': 'test'}],
            'processes': [
                {
                    'name': 'crasher',
                    'group': 'test',
                    'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.rapid_crasher 1 1',
                    'auto_start': True,
                    'start_retries': 2,
                },
            ],
        })

        self.start_supervisor(config)

        # Wait for process to run and crash
        time.sleep(3.0)

        # HTTP should still work
        conn = http.client.HTTPConnection('localhost', self.http_port, timeout=5)
        try:
            conn.request('GET', '/')
            resp = conn.getresponse()

            # Should succeed
            self.assertEqual(resp.status, 200)

            data = json.loads(resp.read())
            self.assertIn('groups', data)

        finally:
            conn.close()
